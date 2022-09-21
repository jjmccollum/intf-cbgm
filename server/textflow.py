#!/usr/bin/python3
# -*- encoding: utf-8 -*-

"""The API server for CBGM.  The textflow and stemmata diagrams."""

import collections

import flask
from flask import request, current_app
import flask_login
import networkx as nx

from ntg_common import tools
from ntg_common import db_tools
from ntg_common.db_tools import execute
from ntg_common.cbgm_common import CBGM_Params, bitarray_count_by_range, \
    create_labez_matrix, calculate_mss_similarity_preco, calculate_mss_similarity_postco

from login import auth, user_can_write
import helpers
from helpers import parameters, Passage, get_excluded_ms_ids, \
     make_dot_response, make_png_response
from checks import congruence

import numpy as np # to support selection and partial sorting of an array of potential-ancestor relationships
from bitarray import bitarray # support for dynamic bit arrays, which can be modified after initialization (useful for set cover/substemma optimization) and are used to construct succinct data structures


bp = flask.Blueprint ('textflow', __name__)


def init_app (_app):
    """ Initialize the flask app. """


SHAPES = {
    'a' : 'ellipse',
    'b' : 'box',
    'c' : 'pentagon',
    'd' : 'hexagon',
    'e' : 'septagon',
    'f' : 'octagon',
    'g' : 'diamond',
    'h' : 'trapezium',
    'i' : 'parallelogram',
    'j' : 'house',
    'k' : 'invtrapezium',
    'l' : 'invparallelogram',
    'm' : 'invhouse',
}


def remove_z_leaves (graph):
    """ Removes leaves (recursively) if they read z. """

    # We cannot use DFS because we don't know the root.
    try:
        nodes = list (nx.topological_sort (graph))
    except nx.NetworkXUnfeasible:
        return

    for n in reversed (nodes):
        atts = graph.nodes[n]
        if graph.out_degree (n) == 0 and 'labez' in atts and atts['labez'][0] == 'z':
            graph.remove_node (n)


def textflow (passage_or_id, range_start = None, range_end = None):
    """ Output a textual flow digram of manuscripts. 
    
    Optionally, start and end range of passage indices (which are expected to be 0-based numerical indices)
    can be specified, in which case textual flow ancestors will be calculated only on the basis of that range of passages.
    """

    labez        = request.args.get ('labez') or ''             # reading index; if not specified, the global textual flow may be desired
    hyp_a        = request.args.get ('hyp_a') or 'A'            # ID of the witness to treat as the hyparchetype; if not specified, then the Ausgangstext is used 
    connectivity = int (request.args.get ('connectivity') or 10)# connectivity limit
    width        = float (request.args.get ('width') or 0.0)    
    fontsize     = float (request.args.get ('fontsize') or 10.0)
    mode         = request.args.get ('mode') or 'sim'

    include      = request.args.getlist ('include[]')   or []   # normally excluded witnesses to include
    fragments    = request.args.getlist ('fragments[]') or []   # fragmentary witnesses included
    checks       = request.args.getlist ('checks[]') or []      # congruence checks
    var_only     = request.args.getlist ('var_only[]')  or []   # only include edges where variation occurs (used for Coherence in Variant Attestations calculation)
    cliques      = request.args.getlist ('cliques[]')   or []   # should split attestatations be treated separately?

    fragments = 'fragments' in fragments  # True if any fragmentary (i.e., less than half extant) witnesses are included
    checks    = 'checks'    in checks     # True if congruence checks are enabled
    var_only  = 'var_only'  in var_only   # Panel: Coherence at Variant Passages (GraphViz)
    cliques   = 'cliques'   in cliques    # consider or ignore cliques
    leaf_z    = 'Z'         in include    # show leaf z nodes in global textflow?

    view = 'affinity_view' if mode == 'rec' else 'affinity_p_view'

    global_textflow = not ((labez != '') or var_only)
    rank_z = False  # include z nodes in ranking?

    if global_textflow:
        connectivity = 1
        rank_z = True
    if connectivity == 21:
        connectivity = 9999

    graph = nx.DiGraph () # the textual flow graph we want to generate
    ranks = [] # a list of objects with entries for ms1, ms2, and the rank of m2 as a potential ancestor of ms1.

    labez_where = ''
    frag_where = ''
    z_where = ''

    if labez != '':
        labez_where = 'AND app.cbgm AND app.labez = :labez'
        if hyp_a != 'A':
            labez_where = 'AND app.cbgm AND (app.labez = :labez OR (app.ms_id = 1 AND :hyp_a = :labez))'

    if not fragments:
        frag_where = 'AND a.common > a.ms1_length / 2' # should "a" be "app" here?

    if not rank_z:
        z_where = "AND app.labez !~ '^z' AND app.certainty = 1.0"

    group_field = 'labez_clique' if cliques else 'labez'

    # NOTE from Joey: In this template for the new code, the CBGM_Params instance that includes the necessary bit arrays will be built from scratch.
    # In terms of performance, it would probably be faster to serialize these bit arrays, write them to the affinities table when the cbgm.py script is first run,
    # and read them from the affinities table here as the old code does. The tradeoff is that the size of the affinities table would scale as O(n_mss² * n_passages) instead of O(n_mss²).

    # To avoid messing with the DB connection once it's already open, populate the CBGM_Params instance here if we are dealing with a subrange of passages:
    val = CBGM_Params ()
    parameters = dict ()
    if range_start is not None or range_end is not None:
        create_labez_matrix (current_app.config.dba, parameters, val) # populate a matrix of readings for witnesses at all units
        calculate_mss_similarity_preco (current_app.config.dba, parameters, val) # populate PASS and EQ bitarray matrices
        calculate_mss_similarity_postco (current_app.config.dba, parameters, val) # populate PRIOR and other bitarray matrices

    with current_app.config.dba.engine.begin () as conn:
        passage = Passage (conn, passage_or_id)
        rg_id   = passage.request_rg_id (request)

        exclude = get_excluded_ms_ids (conn, include)

        # nodes query
        #
        # get all nodes or all nodes (hypothetically) attesting labez

        res = execute (conn, """
        SELECT ms_id
        FROM apparatus app
        WHERE pass_id = :pass_id AND ms_id NOT IN :exclude {labez_where} {z_where}
        """, dict (parameters, exclude = exclude,
                pass_id = passage.pass_id, labez = labez,
                hyp_a = hyp_a, labez_where = labez_where, z_where = z_where))

        nodes = { row[0] for row in res }
        if not nodes:
            nodes = { -1 } # avoid SQL syntax error

        # NOTE from Joey: To avoid changing too much old code, I have placed the old and new code in separate if-blocks based on whether specific passage ranges have been specified.
        ranks = []
        if range_start is None and range_end is None:
            # Old code continues here

            # rank query
            #
            # query to get the closest ancestors for every node with rank <= connectivity

            query = """
            SELECT ms_id1, ms_id2, rank
            FROM (
            SELECT ms_id1, ms_id2, rank () OVER (PARTITION BY ms_id1
                ORDER BY affinity DESC, common, older, newer DESC, ms_id2) AS rank
            FROM {view} a
            WHERE ms_id1 IN :nodes AND a.rg_id = :rg_id AND ms_id2 NOT IN :exclude
                AND newer > older {frag_where}
            ) AS r
            WHERE rank <= :connectivity
            ORDER BY rank
            """

            res = execute (conn, query,
                        dict (parameters, nodes = tuple (nodes), exclude = exclude,
                                rg_id = rg_id, pass_id = passage.pass_id, view = view,
                                labez = labez, connectivity = connectivity,
                                frag_where = frag_where, hyp_a = hyp_a))

            Ranks = collections.namedtuple ('Ranks', 'ms_id1 ms_id2 rank')
            ranks = list (map (Ranks._make, res))
        else:
            # New code continues here
            # If we are determining textual flow ancestry based on a subrange of passages, 
            # then we cannot impose the constraint newer > older in the query (since these counts are based on all passages)
            # and sort the genealogical relationships returned from the query by general affinity (which is also calculated based on all passages)
            # and pick the top ones within the connectivity limit.
            # Instead, for each witness in the nodes set, we must retrieve the EQ and PRIOR bitarrays for all other witnesses in the nodes set relative to it,
            # calculate the number of agreements and prior readings for the other witnesses at the subrange of passages,
            # and select the top connectivity_limit bitarrays according to affinity (breaking ties as above).
            Ranks = collections.namedtuple ('Ranks', 'ms_id1 ms_id2 rank')
            # If either end of the passage range is empty, then set it explicitly:
            if range_start is None:
                range_start = 0
            if range_end is None:
                range_end = val.n_passages - 1
            for ms_id1 in nodes:
                # Initialize a list of (descendant_id, ancestor_id, affinity, eq, prior, posterior) entries for this descendant:
                relationships = []
                for ms_id2 in nodes:
                    extant = val.pass_bitarrays[(ms_id1, ms_id2)]
                    num_extant = bitarray_count_by_range(extant, range_start, range_end)
                    # If there are no passages in this range where both witnesses are extant, then they cannot be related here; skip this relationship:
                    if num_extant == 0:
                        continue
                    eq = val.eq_bitarrays[(ms_id1, ms_id2)]
                    num_eq = bitarray_count_by_range(eq, range_start, range_end)
                    affinity = num_eq / num_extant
                    prior = val.prior_bitarrays[(ms_id1, ms_id2)]
                    num_prior = bitarray_count_by_range(prior, range_start, range_end)
                    posterior = val.prior_bitarrays[(ms_id2, ms_id1)]
                    num_posterior = bitarray_count_by_range(posterior, range_start, range_end)
                    # If ms1 has at least as many prior readings than ms2 at the passages in the desired range, then m2 cannot be a potential ancestor; skip it:
                    if num_prior >= num_posterior:
                        continue
                    # Otherwise, populate a genealogical relationship record with this data
                    # and add it to the list for this witness: 
                    relationship = tuple([ms_id1, ms_id2, affinity, num_eq, num_prior, num_posterior])
                    relationships.append(relationship)
                # Then convert this list of potential ancestry relationships to a NumPy structured array:
                relationships_array = np.array(relationships, dtype=[("ms_id1", "i4"), ("ms_id2", "i4"), ("affinity", "f4"), ("eq", "i4"), ("prior", "i4"), ("posterior", "i4")]) # 32-bit float for affinity, 32-bit ints for everything else
                # If this array is longer than the connectivity limit, then partition in-place (without sorting it, to save time)
                # so that the closest relationships within the connectivity limit occur in the last few positions,
                # and keep only the relationships within the connectivity limit:
                if len(relationships_array) > connectivity_limit:
                    relationships_array.partition(relationships, kth=-connectivity_limit, order=["affinity", "eq", "prior", "posterior"])
                    relationships_array = relationships_array[-connectivity_limit:]
                # Now sort the remaining entries in descending order of the same fields used for the partition.
                # NOTE: Sorting is not strictly necessary, but I am implementing it here to satisfy the assumptions of the node-connecting procedure below.
                relationships_array.sort(order=["affinity", "eq", "prior", "posterior"])
                relationships_array = np.flip(relationships_array) # NumPy only sorts in ascending order, to reverse the sorted array
                # Then store the resulting relationship entries in namedtuple classes:
                for i, relationship in enumerate(relationships_array):
                    rank = Ranks._make([relationship["ms_id1"], relationship["ms_id2"], i+1]) # use i + 1 for rank because rank is one-based
                    ranks.append(rank)

        # Initially build an unconnected graph with one node for each
        # manuscript.  We will connect the nodes later.  Finally we will remove
        # unconnected nodes.

        graph = nx.DiGraph ()

        dest_nodes = { r.ms_id1 for r in ranks } # set of destination/descendant nodes
        src_nodes  = { r.ms_id2 for r in ranks } # set of source/ancestor nodes

        res = execute (conn, """
        SELECT ms.ms_id, ms.hs, ms.hsnr, a.labez, a.clique, a.labez_clique, a.certainty
        FROM apparatus_view_agg a
        JOIN manuscripts ms USING (ms_id)
        WHERE pass_id = :pass_id AND ms_id IN :ms_ids
        """, dict (parameters,
                ms_ids = tuple (src_nodes | dest_nodes | nodes),
                pass_id = passage.pass_id))

        Mss = collections.namedtuple ('Mss', 'ms_id hs hsnr labez clique labez_clique certainty')
        mss = list (map (Mss._make, res))

        for ms in mss:
            attrs = {}
            attrs['hs']           = ms.hs
            attrs['hsnr']         = ms.hsnr
            attrs['labez']        = ms.labez if ms.certainty == 1.0 else 'zw ' + ms.labez
            attrs['clique']       = ms.clique
            attrs['labez_clique'] = ms.labez_clique if ms.certainty == 1.0 else 'zw ' + ms.labez_clique
            attrs['ms_id']        = ms.ms_id
            attrs['label']        = ms.hs
            attrs['certainty']    = ms.certainty
            attrs['clickable']    = '1'
            if ms.ms_id == 1 and hyp_a != 'A':
                attrs['labez']        = hyp_a[0]
                attrs['clique']       = ''
                attrs['labez_clique'] = hyp_a[0]
            # FIXME: attrs['shape'] = SHAPES.get (attrs['labez'], SHAPES['a'])
            graph.add_node (ms.ms_id, **attrs)

    # Connect the nodes
    #
    # Step 1: If the node has internal parents, keep only the top-ranked
    # internal parent.
    #
    # Step 2: If the node has no internal parents, keep the top-ranked
    # parents for each external attestation.
    #
    # Assumption: ranks are sorted top-ranked first

    def is_z_node (n):
        labez = n['labez']
        cert  = n['certainty']
        return (labez[0] == 'z') or (cert < 1.0)

    tags = set ()
    for step in (1, 2):
        for r in ranks:
            a1 = graph.nodes[r.ms_id1]
            if not r.ms_id2 in graph.nodes:
                continue
            a2 = graph.nodes[r.ms_id2]
            if not (global_textflow) and is_z_node (a2):
                # disregard zz / zw
                continue
            if step == 1 and a1[group_field] != a2[group_field]:
                # differing attestations are handled in step 2
                continue
            if r.ms_id1 in tags:
                # an ancestor of this node that lays within the node's
                # attestation was already seen.  we need not look into other
                # attestations
                continue
            if str (r.ms_id1) + a2[group_field] in tags:
                # an ancestor of this node that lays within this attestation
                # was already seen.  we need not look into further nodes
                continue
            # add a new parent
            if r.rank > 1:
                graph.add_edge (r.ms_id2, r.ms_id1, rank = r.rank, headlabel = r.rank)
            else:
                graph.add_edge (r.ms_id2, r.ms_id1)

            if a1[group_field] == a2[group_field]:
                # tag: has ancestor node within the same attestation
                tags.add (r.ms_id1)
            else:
                # tag: has ancestor node with this other attestation
                tags.add (str (r.ms_id1) + a2[group_field])

    if not leaf_z:
        remove_z_leaves (graph)

    # the if clause fixes #83
    graph.remove_nodes_from ([n for n in nx.isolates (graph)
                                if graph.nodes[n]['labez'] != labez])

    if var_only:
        # Panel: Coherence at Variant Passages (GraphViz)
        #
        # if one predecessor is within the same attestation then remove all
        # other predecessors that are not within the same attestation
        for n in graph:
            within = False
            attestation_n = graph.nodes[n][group_field]
            for p in graph.predecessors (n):
                if graph.nodes[p][group_field] == attestation_n:
                    within = True
                    break
            if within:
                for p in graph.predecessors (n):
                    if graph.nodes[p][group_field] != attestation_n:
                        graph.remove_edge (p, n)

        # remove edges between nodes within the same attestation
        for u, v in list (graph.edges ()):
            if graph.nodes[u][group_field] == graph.nodes[v][group_field]:
                graph.remove_edge (u, v)

        # remove now isolated nodes
        graph.remove_nodes_from (list (nx.isolates (graph)))

        # unconstrain backward edges (yields a better GraphViz layout)
        for u, v in graph.edges ():
            if graph.nodes[u][group_field] > graph.nodes[v][group_field]:
                graph.adj[u][v]['constraint'] = 'false'

    else:
        for n in graph:
            # Use a different label if the parent's labez_clique differs from this
            # node's labez_clique.
            pred = list (graph.predecessors (n))
            attrs = graph.nodes[n]
            if not pred:
                attrs['label'] = "%s: %s" % (attrs['labez_clique'], attrs['hs'])
            for p in pred:
                if attrs['labez_clique'] != graph.nodes[p]['labez_clique']:
                    attrs['label'] = "%s: %s" % (attrs['labez_clique'], attrs['hs'])
                    graph.adj[p][n]['style'] = 'dashed'

    if checks:
        for rank in congruence (conn, passage):
            try:
                graph.adj[rank.ms_id1][rank.ms_id2]['style'] = 'bold'
            except KeyError:
                pass

    if var_only:
        dot = helpers.nx_to_dot_subgraphs (graph, group_field, width, fontsize)
    else:
        dot = helpers.nx_to_dot (graph, width, fontsize)
    return dot


@bp.route ('/textflow.dot/<passage_or_id>')
def textflow_dot (passage_or_id):
    """ Return a textflow diagram in .dot format. """

    auth ()

    dot = textflow (passage_or_id)
    dot = tools.graphviz_layout (dot)
    return make_dot_response (dot)


@bp.route ('/textflow.png/<passage_or_id>')
def textflow_png (passage_or_id):
    """ Return a textflow diagram in .png format. """

    auth ()

    dot = textflow (passage_or_id)
    png = tools.graphviz_layout (dot, format = 'png')
    return make_png_response (png)


def stemma (passage_or_id):
    """Serve a local stemma in dot format.

    A local stemma is a DAG (directed acyclic graph).  The layout of the DAG is
    precomputed on the server using GraphViz.  GraphViz adds a precomputed
    position to each node and a precomputed bezier path to each edge.

    N.B. I also considered client-side layout of DAGs, but found only 2 viable
    libraries:

    - dagre.  Javascript clone of GraphViz.  Unmaintained.  Buggy.  Does not
      work well with require.js.

    - viz.js.  GraphViz cross-compiled to Javascript with Emscripten.  Huge.
      Promising but still early days.

    Both libraries have their drawbacks so the easiest way out was to precompute
    the layout on the server.

    """

    width    = float (request.args.get ('width') or 0.0)
    fontsize = float (request.args.get ('fontsize') or 10.0)

    with current_app.config.dba.engine.begin () as conn:
        passage = Passage (conn, passage_or_id)
        graph = db_tools.local_stemma_to_nx (
            conn, passage.pass_id, user_can_write (current_app)
        )
        dot = helpers.nx_to_dot (graph, width, fontsize, nodesep = 0.2)
        return dot


@bp.route ('/stemma.dot/<passage_or_id>')
def stemma_dot (passage_or_id):
    """ Return a local stemma diagram in .dot format. """

    auth ()

    dot = stemma (passage_or_id)
    dot = tools.graphviz_layout (dot)
    return make_dot_response (dot)


@bp.route ('/stemma.png/<passage_or_id>')
def stemma_png (passage_or_id):
    """ Return a local stemma diagram in .png format. """

    auth ()

    dot = stemma (passage_or_id)
    png = tools.graphviz_layout (dot, format = 'png')
    return make_png_response (png)
