# -*- encoding: utf-8 -*-

"""Common routines for the CBGM.

"""

import collections
import logging

import networkx as nx
import numpy as np
from bitarray import bitarray

from ntg_common import db_tools
from ntg_common.db_tools import execute, executemany, executemany_raw
from ntg_common.tools import log

"""
Notes from Joey McCollum, 2022/09/19:

I've added an import statement for the bitarray library, which offers support for dynamic bit arrays.
These are compact data structures which can be (de)serialized as bytes in the affinities table of the database.
By encoding shared extant passages (PASS), agreements (EQ), prior readings (W1>W2), posterior readings (W1<W2), 
unrelated readings (UNREL), and unclear relationships (UNCL) between witnesses at all passages in bit arrays,
with a position for each passage, we can quickly retrieve all genealogical relationships between any two witnesses.
This is important for dynamic textual flow computation
(where we may have to recalculate potential ancestry relationships based on specific ranges of passages)
and substemma optimization (which reduces to a set cover problem whose heuristic solution can be accelerated with bit arrays).
The matrices in the CBGM_Params class populated by the methods in this module could be populated using these bit arrays,
using the bitarray.count() method to get counts of different types of relationships.
(This could replace the count_by_range method defined in this module.)

For now, I have only added code to write the bit arrays to the affinities table.
"""


class CBGM_Params ():
    """ Structure that holds intermediate results of the CBGM. """

    n_mss = 0
    "No. of manuscripts"

    n_passages = 0
    "No. of passages"

    n_ranges = 0
    "No. of ranges"

    ranges = None
    "list of (named tuple Range)"

    variant_matrix = None
    """Boolean (1 x passages) matrix of invariant passages.  We will need this the
    day we decide *not* to eliminate all invariant readings from the
    database.

    """

    labez_matrix = None
    """Integer matrix (mss x passages) of labez.  Each entry represents one reading:
    0 = lacuna, 1 = 'a', 2 = 'b', ...  Used by the pre-coherence computations.

    """

    def_matrix = None
    """Boolean matrix (mss x passages) set if ms. is defined at passage."""

    and_matrix = None
    """Integer matrix (ranges x mss x mss) with counts of the passages that are
    defined in both mss.

    """

    eq_matrix = None
    """Integer matrix (ranges x mss x mss) with counts of the passages that are
    equal in both mss.

    """

    parent_matrix = None
    """Integer matrix (ranges x mss x mss) with counts of the passages that are
    older in ms1 than in ms2, using only immediate descendence.  This matrix is
    asymmetrical.

    """

    ancestor_matrix = None
    """Integer matrix (ranges x mss x mss) with counts of the passages that are
    older in ms1 than in ms2.  This matrix is asymmetrical.

    """

    unclear_parent_matrix = None
    """Integer matrix (ranges x mss x mss) with counts of the passages whose
    relationship is unclear in ms1 and ms2, using only immediate descendence.

    """

    unclear_ancestor_matrix = None
    """Integer matrix (ranges x mss x mss) with counts of the passages whose
    relationship is unclear in ms1 and ms2.

    """

    # Joey's proposed additions/replacements follow:
    pass_bitarrays = None
    """A dictionary mapping (ms1_id, ms2_id) tuples to bitarrays, where each bitarray has a position for each passage
    and a bit in that position is set if the manuscripts corresponding to the row and column indices 
    are both extant at that passage.
    Note that the entries along the diagonal, where the row and column represent the same manuscript, 
    indicate the extant passages of that manuscript by itself.
    """

    eq_bitarrays = None
    """A dictionary mapping (ms1_id, ms2_id) tuples to bitarrays, where each bitarray has a position for each passage
    and a bit in that position is set if the manuscripts corresponding to the row and column indices 
    have the same reading at that passage.
    """

    parent_bitarrays = None
    """A dictionary mapping (ms1_id, ms2_id) tuples to bitarrays, where each bitarray has a position for each passage
    and a bit in that position is set if the manuscripts corresponding to the row index
    has a reading directly prior to that of the manuscript corresponding to the column index
    (i.e., if there is one edge from the first manuscript's reading to the second manuscript's reading in the local stemma).
    """

    prior_bitarrays = None
    """A dictionary mapping (ms1_id, ms2_id) tuples to bitarrays, where each bitarray has a position for each passage
    and a bit in that position is set if the manuscript corresponding to the row index 
    has a reading prior to that of the manuscript corresponding to the column index.
    """

    norel_bitarrays = None
    """A dictionary mapping (ms1_id, ms2_id) tuples to bitarrays, where each bitarray has a position for each passage
    and a bit in that position is set if the manuscripts corresponding to the row and column indices
    have readings with a common ancestor in the local stemma that is neither of those readings
    (i.e., if their readings are known to be independent and therefore have no directed relationship).
    """

    uncl_bitarrays = None
    """A dictionary mapping (ms1_id, ms2_id) tuples to bitarrays, where each bitarray has a position for each passage
    and a bit in that position is set if the manuscripts corresponding to the row and column indices
    have readings with no common ancestor in the local stemma.
    Note that this relation can only hold if the local stemma is disconnected 
    (i.e., if there are readings whose source is unclear, meaning that they have the first bit for "?" set in their mask).
    """



def create_labez_matrix (dba, parameters, val):
    """Create the :attr:`labez matrix <scripts.cceh.cbgm.CBGM_Params.labez_matrix>`."""

    with dba.engine.begin () as conn:

        np.set_printoptions (threshold = 30)

        # get number of all passages (including invariant ones)
        res = execute (conn, """
        SELECT count (*)
        FROM passages
        """, parameters)
        val.n_passages = res.fetchone ()[0]

        # get matrix of invariant passages
        # Initialize all passages to 'variant'
        variant_matrix = np.ones ((1, val.n_passages), np.bool_)

        res = execute (conn, """
        SELECT pass_id - 1
        FROM passages
        WHERE NOT (variant)
        """, parameters)

        for row in res:
            variant_matrix [0, row[0]] = False
        val.variant_matrix = variant_matrix

        # get no. of manuscripts
        res = execute (conn, """
        SELECT count (*)
        FROM manuscripts
        """, parameters)
        val.n_mss = res.fetchone ()[0]

        # get no. of ranges
        Range = collections.namedtuple ('Range', 'rg_id range start end')
        res = execute (conn, """
        SELECT rg_id, range, MIN (pass_id) - 1 AS first_id, MAX (pass_id) AS last_id
        FROM ranges ch
        JOIN passages p ON ch.passage @> p.passage
        GROUP BY rg_id, range
        ORDER BY lower (ch.passage), upper (ch.passage) DESC
        """, parameters)
        val.n_ranges = res.rowcount
        val.ranges = list (map (Range._make, res))
        log (logging.INFO, '  No. of ranges: ' + str (val.n_ranges))

        # Matrix ms x pass

        # Initialize all manuscripts to the labez 'a'
        labez_matrix  = np.broadcast_to (np.array ([1], np.uint32), (val.n_mss, val.n_passages)).copy ()

        # overwrite matrix where actual labez is not 'a'
        res = execute (conn, """
        SELECT ms_id - 1, pass_id - 1, ord_labez (labez) as labez
        FROM apparatus a
        WHERE labez != 'a' AND cbgm
        """, parameters)

        for row in res:
            labez_matrix [row[0], row[1]] = row[2] # i.e., labez_matrix[ms index, passage index] = reading index

        # clear matrix where reading is uncertain
        res = execute (conn, """
        SELECT DISTINCT ms_id - 1, pass_id - 1
        FROM apparatus
        WHERE certainty != 1.0
        """, parameters)

        for row in res:
            labez_matrix [row[0], row[1]] = 0 # i.e., labez_matrix[ms index, passage index] = 0 (index of ? placeholder)

        val.labez_matrix = labez_matrix

        # Boolean matrix ms x pass set where passage is defined
        val.def_matrix = np.greater (val.labez_matrix, 0)
        val.def_matrix = np.logical_and (val.def_matrix, val.variant_matrix) # mask invariant passages

        log (logging.INFO, '  Size of the labez matrix: ' + str (val.labez_matrix.shape))


def count_by_range (a, range_starts, range_ends):
    """Count true bits in array ranges

    Count the bits that are true in multiple ranges of the same array of booleans.

    :param numpy.Array a:      Input array
    :type a: np.Array of np.bool:
    :param int[] range_starts: Starting offsets of the ranges to count.
    :param int[] range_ends:   Ending offsets of the ranges to count.

    """
    cs = np.cumsum (a)    # cs[0] = a[0], cs[1] = cs[0] + a[1], ..., cs[n] = total
    cs = np.insert (cs, 0, 0)
    cs_start = cs[range_starts] # get the sums at the range beginnings
    cs_end   = cs[range_ends]   # get the sums at the range ends
    return cs_end - cs_start


def calculate_mss_similarity_preco (_dba, _parameters, val):
    r"""Calculate pre-coherence mss similarity

    The pre-coherence similarity is defined as:

    .. math::

        \mbox{similarity}=\frac{\mbox{equal passages}}{\mbox{passages in common}}

    ..

        Kapitelweise füllen auf Basis von Vergleichen einzelner
        Variantenspektren in ECM_Acts_Sp.  Vergleich von je zwei Handschriften:
        An wieviel Stellen haben sie gemeinsam Text, an wieviel Stellen stimmen
        sie überein bzw. unterscheiden sie sich (inklusive Quotient)?  Die
        Informationen werden sowohl auf Kapitel- wie auch Buchebene
        festgehalten.

        --VGA/VG05_all3.pl

    """

    # Matrix range x ms x ms with count of the passages that are defined in both mss
    val.and_matrix = np.zeros ((val.n_ranges, val.n_mss, val.n_mss), dtype = np.uint16)

    # Matrix range x ms x ms with count of the passages that are equal in both mss
    val.eq_matrix  = np.zeros ((val.n_ranges, val.n_mss, val.n_mss), dtype = np.uint16)

    # Dictionary mapping (ms1_id, ms2_id) tuples to bitarrays of passages (over the entire book, not divided into ranges) that are defined in both mss
    val.pass_bitarrays = {}
    
    # Dictionary mapping (ms1_id, ms2_id) tuples to bitarrays of passages (over the entire book, not divided into ranges) where both mss agree
    val.eq_bitarrays = {}

    val.range_starts = [ch.start for ch in val.ranges]
    val.range_ends   = [ch.end   for ch in val.ranges]

    # pre-genealogical coherence outputs symmetrical matrices
    # loop over all mss O(n_mss² * n_ranges * n_passages)

    for j in range (0, val.n_mss):
        labezj = val.labez_matrix[j]
        defj   = val.def_matrix[j]

        for k in range (j + 1, val.n_mss):
            labezk = val.labez_matrix[k]
            defk   = val.def_matrix[k]

            def_and  = np.logical_and (defj, defk)
            labez_eq = np.logical_and (def_and, np.equal (labezj, labezk))

            val.and_matrix[:,j,k] = val.and_matrix[:,k,j] = count_by_range (def_and, val.range_starts, val.range_ends)
            val.eq_matrix[:,j,k]  = val.eq_matrix[:,k,j]  = count_by_range (labez_eq, val.range_starts, val.range_ends)

            val.pass_bitarrays[(j, k)] = bitarray(def_and)
            val.eq_bitarrays[(j, k)] = bitarray(labez_eq)


def calculate_mss_similarity_postco (dba, parameters, val, do_checks = True):
    """Calculate post-coherence mss similarity

    Genealogical coherence outputs asymmetrical matrices.
    Loop over all mss O(n_mss² * n_ranges * n_passages).

    The main idea in this function is to get the DAG (directed acyclic graph)
    into a representation that can be used by numpy.  Numpy gives us a
    tremendous speed boost.

    For every passage and every reading we build

    - a bitmask for the reading and
    - a bitmask for all prior readings of this reading.

    Then for every passage and every manuscript we look up what the manuscript
    offers and store the relative bitmasks in 2 matrices.

    For illustration we refer to this passage (Mc 10:10/16-22 pass_id == 3240):

    .. pic:: dot
       :file: local-stemma-mark-3240.dot
       :align: center

    In a first step every reading (labez and clique) gets assigned a bitmask:

    .. code-block:: none

       labez | clique |                               mask
       ------+--------+-----------------------------------------------------------------
       ?     |        | 0000000000000000000000000000000000000000000000000000000000000001
       a     | 1      | 0000000000000000000000000000000000000000000000000000000000000010
       a     | 2      | 0000000000000000000000000000000000000000000000000000000000000100
       b     | 1      | 0000000000000000000000000000000000000000000000000000000000001000
       c     | 1      | 0000000000000000000000000000000000000000000000000000000000010000
       c     | 2      | 0000000000000000000000000000000000000000000000000000000000100000
       c     | 3      | 0000000000000000000000000000000000000000000000000000000001000000
       d     | 1      | 0000000000000000000000000000000000000000000000000000000010000000
       d     | 2      | 0000000000000000000000000000000000000000000000000000000100000000
       e     | 1      | 0000000000000000000000000000000000000000000000000000001000000000
       f     | 1      | 0000000000000000000000000000000000000000000000000000010000000000
       f     | 2      | 0000000000000000000000000000000000000000000000000000100000000000
       g     | 1      | 0000000000000000000000000000000000000000000000000001000000000000
       h     | 1      | 0000000000000000000000000000000000000000000000000010000000000000
       i     | 1      | 0000000000000000000000000000000000000000000000000100000000000000
       j     | 1      | 0000000000000000000000000000000000000000000000001000000000000000
       k     | 1      | 0000000000000000000000000000000000000000000000010000000000000000
       l     | 1      | 0000000000000000000000000000000000000000000000100000000000000000
       m     | 1      | 0000000000000000000000000000000000000000000001000000000000000000
       n     | 1      | 0000000000000000000000000000000000000000000010000000000000000000
       o     | 1      | 0000000000000000000000000000000000000000000100000000000000000000
       p     | 1      | 0000000000000000000000000000000000000000001000000000000000000000
       q     | 1      | 0000000000000000000000000000000000000000010000000000000000000000
       r     | 1      | 0000000000000000000000000000000000000000100000000000000000000000
       s     | 1      | 0000000000000000000000000000000000000001000000000000000000000000
       t     | 1      | 0000000000000000000000000000000000000010000000000000000000000000
       u     | 1      | 0000000000000000000000000000000000000100000000000000000000000000
       v     | 1      | 0000000000000000000000000000000000001000000000000000000000000000
       v     | 2      | 0000000000000000000000000000000000010000000000000000000000000000
       v     | 3      | 0000000000000000000000000000000000100000000000000000000000000000
       w     | 1      | 0000000000000000000000000000000001000000000000000000000000000000

    Note that we have an extra bitmask for '?'.  This allows quick testing for
    unknown origin.

    In the second step we build the ancestor bitmasks.

    Reading 'f' has prior readings 'c', 'm', and 'a'.  Thus the ancestor bitmask
    for reading 'f' is the bitwise_or of the masks for 'c', 'm', and 'a':

    .. code-block:: none

       labez | clique |                               mask
       ------+--------+-----------------------------------------------------------------
       c     | 1      | 0000000000000000000000000000000000000000000000000000000000010000
       m     | 1      | 0000000000000000000000000000000000000000000001000000000000000000
       a     | 1      | 0000000000000000000000000000000000000000000000000000000000000010

       labez | clique |                            ancestor mask
       ------+--------+-----------------------------------------------------------------
       f     | 1      | 0000000000000000000000000000000000000000000001000000000000010010

    Another example: Reading 'w' has prior readings 'a2', 'a2' is of unknown
    origin. The ancestor mask for 'w' is the bitwise_or of the masks for 'a2' and '?':

    .. code-block:: none

       labez | clique |                               mask
       ------+--------+-----------------------------------------------------------------
       a     | 2      | 0000000000000000000000000000000000000000000000000000000000000100
       ?     |        | 0000000000000000000000000000000000000000000000000000000000000001

       labez | clique |                            ancestor mask
       ------+--------+-----------------------------------------------------------------
       w     | 1      | 0000000000000000000000000000000000000000000000000000000000000101

    After building the masks for every reading at every passage we put the masks
    into 2 matrices of dimension (mss x passages), the mask_matrix and the
    ancestor_matrix.  The mask_matrix contains the mask for the reading the
    manuscript offers, the ancestor_matrix contains the ancestor mask for that reading.

    Manuscript 1457 (ms_id == 156) (at pass_id == 3240) reads 'c', so the
    mask_matrix contains:

    .. code-block::

       mask_matrix[156,3240] = b'0000000000000000000000000000000000000000000000000000000000010000'

    Manuscript 706 (ms_id == 102) (at pass_id == 3240) reads 'f', so the
    ancestor_matrix contains:

    .. code-block::

       ancestor_matrix[102,3240] = b'0000000000000000000000000000000000000000000001000000000000010010'

    To test for ancestrality between mss. 1457 and 706 we do a bitwise_and of the
    mask_matrix of 1457 and the ancestor_matrix of 706. If the result is non-zero then
    1457 is ancestral to 706.

    (Question from Joey: If the first bit corresponds to an unknown relationship, 
    then shouldn't we be checking if the bitwise_and is greater than 1 rather than 0?
    What if more than one reading is of unknown origin and therefore the ? placeholder is an "ancestor reading" to both?)

    .. code-block::

       is_ancestral = np.bitwise_and (mask_matrix[156,3240], ancestor_matrix[102,3240]) > 0

    But that would be very slow.  Numpy allows to operate on whole matrix rows
    at a time so we can calculate the ancestrality for all passages with a
    single call to numpy.

    .. code-block::

       is_ancestral = np.bitwise_and (mask_matrix[156], ancestor_matrix[102]) > 0

    is_ancestral is an array of booleans.  We only have to count how many
    elements of it are True to obtain the number of prior readings.

    Reversing the role of the two manuscripts (mask_matrix and ancestor_matrix)
    gives us the number of posterior readings.

    """

    with dba.engine.begin () as conn:

        # Load all passages into memory

        res = execute (conn, """
        SELECT pass_id, begadr, endadr FROM passages
        ORDER BY pass_id
        """, parameters)

        stemmas = dict ()
        for pass_id, begadr, endadr in res.fetchall ():
            G = db_tools.local_stemma_to_nx (conn, pass_id, True) # True == add isolated roots

            if do_checks:
                # sanity tests
                # connect the graph through a root node for the following tests:
                G.add_node ('root', label = 'root')
                G.add_edge ('root', '*')
                G.add_edge ('root', '?')
                if not nx.is_weakly_connected (G):
                    # use it anyway
                    log (logging.WARNING, "Local Stemma @ %s-%s is not connected (pass_id=%s)." %
                         (begadr, endadr, pass_id))
                if not nx.is_directed_acyclic_graph (G):
                    # don't use these
                    log (logging.ERROR, "Local Stemma @ %s-%s is not a directed acyclic graph (pass_id=%s)." %
                         (begadr, endadr, pass_id))
                    continue
                # ... and remove it again
                G.remove_node ('root')

            G.nodes['*']['mask'] = 0
            G.nodes['?']['mask'] = 1 # bitmask == 1 signifies source is unclear

            # build node bitmasks.  Every node gets a different bit set.
            i = 1
            for n in sorted (G.nodes ()):
                attrs = G.nodes[n]
                attrs['parents'] = 0
                attrs['ancestors'] = 0
                if 'mask' not in attrs:
                    i += 1
                    if i < 64:
                        attrs['mask'] = (1 << i)
                    else:
                        attrs['mask'] = 0
                        # mask is 64 bit only
                        log (logging.ERROR, "Too many cliques in local stemma @ %s-%s (pass_id=%s)." %
                             (begadr, endadr, pass_id))

            # build the parents bit mask. We set the bits of the parent nodes.
            for n in G:
                mask = G.nodes[n]['mask']
                for succ in G.successors (n):
                    G.nodes[succ]['parents'] |= mask

            # build the ancestors mask.  We set the bits of all node ancestors.
            TC = nx.transitive_closure (G)
            for n in TC:
                # transitive_closure does not copy attributes !
                mask = G.nodes[n]['mask']
                for succ in TC.successors (n):
                    G.nodes[succ]['ancestors'] |= mask

            # save the graph for later
            stemmas[pass_id - 1] = G

        # Matrix mss x passages containing the bitmask of the current reading
        mask_matrix     = np.zeros ((val.n_mss, val.n_passages), np.uint64)
        # Matrix mss x passages containing the bitmask of the parent readings
        parent_matrix   = np.zeros ((val.n_mss, val.n_passages), np.uint64)
        # Matrix mss x passages containing the bitmask of the ancestral readings
        ancestor_matrix = np.zeros ((val.n_mss, val.n_passages), np.uint64)

        # load ms x pass
        res = execute (conn, """
        SELECT pass_id - 1 AS pass_id,
               ms_id   - 1 AS ms_id,
               labez_clique (labez, clique) AS labez_clique
        FROM apparatus_cliques_view a
        WHERE labez !~ '^z[u-z]' AND cbgm
        ORDER BY pass_id
        """, parameters)

        LocStemEd = collections.namedtuple ('LocStemEd', 'pass_id ms_id labez_clique')
        rows = list (map (LocStemEd._make, res))

        # If ((current bitmask of ms j) and (ancestor bitmask of ms k) > 0) then
        # ms j is an ancestor of ms k.

        error_count = 0
        for row in rows:
            try:
                attrs = stemmas[row.pass_id].nodes[row.labez_clique]
                mask_matrix     [row.ms_id, row.pass_id] = attrs['mask']
                parent_matrix   [row.ms_id, row.pass_id] = attrs['parents']
                ancestor_matrix [row.ms_id, row.pass_id] = attrs['ancestors']
            except KeyError:
                error_count += 1
                # print (row.pass_id + 1)
                # print (str (e))

        # Matrix mss x passages containing True if source is unclear (s1 = '?')
        quest_matrix = np.bitwise_and (parent_matrix, 1)  # 1 means source unclear

        if error_count:
            log (logging.WARNING, "Could not find labez and clique in LocStem in %d cases." % error_count)
        log (logging.DEBUG, "mask:\n"      + str (mask_matrix))
        log (logging.DEBUG, "parents:\n"   + str (parent_matrix))
        log (logging.DEBUG, "ancestors:\n" + str (ancestor_matrix))
        log (logging.DEBUG, "quest:\n"     + str (quest_matrix))

        def postco (mask_matrix, anc_matrix):

            local_stemmas_with_loops = set ()

            # Matrix range x ms x ms with count of the passages that are older in ms1 than in ms2
            ancestor_matrix = np.zeros ((val.n_ranges, val.n_mss, val.n_mss), dtype = np.uint16)

            # Matrix range x ms x ms with count of the passages whose relationship is unclear in ms1 and ms2
            unclear_matrix  = np.zeros ((val.n_ranges, val.n_mss, val.n_mss), dtype = np.uint16)

            for j in range (0, val.n_mss):
                for k in range (0, val.n_mss):
                    # See: VGA/VGActs_allGenTab3Ph3.pl

                    # set bit if the reading of j is ancestral to the reading of k
                    varidj_is_older = np.bitwise_and (mask_matrix[j], anc_matrix[k]) > 0
                    varidk_is_older = np.bitwise_and (mask_matrix[k], anc_matrix[j]) > 0

                    if j == 0 and k > 0 and varidk_is_older.any ():
                        log (logging.ERROR, "Found varid older than A in msid: %d = %s"
                             % (k, np.nonzero (varidk_is_older)))

                    # error check for loops
                    if do_checks:
                        check = np.logical_and (varidj_is_older, varidk_is_older)
                        if np.any (check):
                            not_check       = np.logical_not (check)
                            varidj_is_older = np.logical_and (varidj_is_older, not_check)
                            varidk_is_older = np.logical_and (varidk_is_older, not_check)

                            local_stemmas_with_loops |= set (np.nonzero (check)[0])

                    # wenn die vergl. Hss. von einander abweichen u. eine von ihnen
                    # Q1 = '?' hat, UND KEINE VON IHNEN QUELLE DER ANDEREN IST, ist
                    # die Beziehung 'UNCLEAR'

                    unclear = np.logical_and (val.def_matrix[j], val.def_matrix[k])
                    unclear = np.logical_and (unclear, np.not_equal (val.labez_matrix[j], val.labez_matrix[k]))
                    unclear = np.logical_and (unclear, np.logical_or (quest_matrix[j], quest_matrix[k]))
                    unclear = np.logical_and (unclear, np.logical_not (np.logical_or (varidj_is_older, varidk_is_older)))

                    ancestor_matrix[:,j,k] = count_by_range (varidj_is_older, val.range_starts, val.range_ends)
                    unclear_matrix[:,j,k]  = count_by_range (unclear, val.range_starts, val.range_ends)

            if local_stemmas_with_loops:
                log (logging.ERROR, "Found loops in local stemmata: %s" % sorted (local_stemmas_with_loops))

            return ancestor_matrix, unclear_matrix

        val.parent_matrix,   val.unclear_parent_matrix   = postco (mask_matrix, parent_matrix)
        val.ancestor_matrix, val.unclear_ancestor_matrix = postco (mask_matrix, ancestor_matrix)

        # Added by Joey: I do the same for the bitarrays below, but I populate all four together

        # Dictionary mapping (ms1_id, ms2_id) tuples to bitarrays of passages (over the entire book, not divided into ranges) where ms1 has a parent reading to that of ms2
        val.parent_bitarrays = {}
        # Dictionary mapping (ms1_id, ms2_id) tuples to bitarrays of passages (over the entire book, not divided into ranges) where ms1 is prior to ms2
        val.prior_bitarrays = {}
        # Dictionary mapping (ms1_id, ms2_id) tuples to bitarrays of passages (over the entire book, not divided into ranges) where ms1 and ms2 are known to be independent
        val.norel_bitarrays = {}
        # Dictionary mapping (ms1_id, ms2_id) tuples to bitarrays of passages (over the entire book, not divided into ranges) where ms1 and ms2 have an unclear relationship
        val.uncl_bitarrays = {}
        # Loop through all (ordered) pairs of witnesses:
        for j in range (0, val.n_mss):
            for k in range (0, val.n_mss):
                # At which passages is the reading of j a parent to the reading of k?
                parent = np.bitwise_and (mask_matrix[j], parent_matrix[k]) > 1 # > 1 because "?" does not explain any other reading
                # At which passages is the reading of j an ancestor to the reading of k?
                prior = np.bitwise_and (mask_matrix[j], ancestor_matrix[k]) > 1 # > 1 because "?" is not prior to any other reading
                # At which passages is the reading of j a descendant of the reading of k?
                posterior = np.bitwise_and (mask_matrix[k], ancestor_matrix[j]) > 1 # > 1 because "?" is not prior to any other reading
                # At which passages are the readings of j and k independent?
                indep = np.logical_and (val.def_matrix[j], val.def_matrix[k]) # both readings must be defined
                indep = np.logical_and (indep, np.not_equal (val.labez_matrix[j], val.labez_matrix[k])) # both readings must be different
                indep = np.logical_and (indep, np.logical_not (np.logical_or (prior, posterior))) # neither reading can be the ancestor to the other
                # At which independent passages does neither reading have "?" as a parent?
                norel = np.logical_and (indep, np.logical_not (np.logical_or (quest_matrix[j], quest_matrix[k])))
                # At which independent passages does at least one reading have "?" as a parent?
                uncl = np.logical_and (indep, np.logical_or (quest_matrix[j], quest_matrix[k]))
                # Now convert these bit lists to bitarrays:
                val.parent_bitarrays[(j, k)] = bitarray(parent)
                val.prior_bitarrays[(j, k)] = bitarray(ancestor)
                val.norel_bitarrays[(j, k)] = bitarray(norel)
                val.uncl_bitarrays[(j, k)] = bitarrays(uncl)


def write_affinity_table (dba, parameters, val):
    """Write back the new affinity (and ms_ranges) tables.
    
    """

    with dba.engine.begin () as conn:
        # perform sanity tests

        # varid older than ms A
        if val.ancestor_matrix[0,:,0].any ():
            log (logging.ERROR, "Found varid older than A in msids: %s"
                 % (np.nonzero (val.ancestor_matrix[0,:,0])))

        # norel < 0
        norel_matrix = (val.and_matrix - val.eq_matrix - val.ancestor_matrix -
                        np.transpose (val.ancestor_matrix, (0, 2, 1)) - val.unclear_ancestor_matrix)
        if np.less (norel_matrix, 0).any ():
            log (logging.ERROR, "norel < 0 in mss. %s"
                 % (np.nonzero (np.less (norel_matrix, 0))))

        # calculate ranges lengths using numpy
        params = []
        for i in range (0, val.n_mss):
            for range_ in val.ranges:
                length = int (np.sum (val.def_matrix[i, range_.start:range_.end]))
                params.append ( { 'ms_id': i + 1, 'range': range_.rg_id, 'length': length } )

        executemany (conn, """
        UPDATE ms_ranges
        SET length = :length
        WHERE ms_id = :ms_id AND rg_id = :range
        """, parameters, params)

        log (logging.INFO, "  Filling Affinity table ...")

        # execute (conn, "TRUNCATE affinity", parameters) # fast but needs access exclusive lock
        execute (conn, "DELETE FROM affinity", parameters)

        for i, range_ in enumerate (val.ranges):
            values = []
            for j in range (0, val.n_mss):
                for k in range (0, val.n_mss):
                    if j != k:
                        common = int (val.and_matrix[i,j,k])
                        equal  = int (val.eq_matrix[i,j,k])
                        if common > 0:
                            values.append ( (
                                range_.rg_id,
                                j + 1,
                                k + 1,
                                float (equal) / common,
                                common,
                                equal,
                                int (val.ancestor_matrix[i,j,k]),
                                int (val.ancestor_matrix[i,k,j]),
                                int (val.unclear_ancestor_matrix[i,j,k]),
                                int (val.parent_matrix[i,j,k]),
                                int (val.parent_matrix[i,k,j]),
                                int (val.unclear_parent_matrix[i,j,k]),
                            ) )

            # speed gain for using executemany_raw: 65s to 55s :-(
            # probably the bottleneck here is string formatting with %s
            executemany_raw (conn, """
            INSERT INTO affinity (rg_id, ms_id1, ms_id2,
                                  affinity, common, equal,
                                  older, newer, unclear,
                                  p_older, p_newer, p_unclear)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, parameters, values)

        log (logging.DEBUG, "eq:"        + str (val.eq_matrix))
        log (logging.DEBUG, "ancestor:"  + str (val.ancestor_matrix))
        log (logging.DEBUG, "unclear:"   + str (val.unclear_ancestor_matrix))
        log (logging.DEBUG, "and:"       + str (val.and_matrix))

# NOTE from Joey: You should be able to accelerate textual flow and other queries if you populate a similar table for the bitarrays that I have added here,
# since deserializing them from table rows is likely to be faster than recalculating them every time 
# through calls to calculate_mss_similarity_preco and calculate_mss_similarity_postco.
# The tradeoff will be that such a table will take (O(n_mss² * n_passages) space (although the bit arrays can be serialized more compactly as bytes or machine words).