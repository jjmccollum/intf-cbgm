# -*- encoding: utf-8 -*-

"""Import databases from mysql.

This script initializes the postgres database and then imports data from one or
more mysql databases.

.. note::

   Make sure to follow the steps in `database-access` first.

The source databases are:

1. a database containing the apparatus of the *Editio Critica Maior*
   publication (ECM),

2. a database containing the *Leitzeile*, and

3. optionally a database containing the editorial decisions regarding the
   priority of the readings (VarGen).

The source tables for Acts are partitioned into 28 chapters.  This is a
historical incident: The software used when the CBGM was first implemented could
not handle big tables.  The import script joins partitioned tables into one.

After running this script you should run the `prepare.py` script.

"""

import argparse
import collections
import logging
import re

import sqlalchemy

from ntg_common import db
from ntg_common import db_tools
from ntg_common.config import args, init_logging, config_from_pyfile
from ntg_common.db_tools import execute, warn, debug
from ntg_common.tools import log


def build_parser ():
    parser = argparse.ArgumentParser (description = __doc__)

    parser.add_argument ('profile', metavar='path/to/file.conf',
                         help="a .conf file (required)")
    parser.add_argument ('-v', '--verbose', dest='verbose', action='count',
                         help='increase output verbosity', default=0)
    return parser


if __name__ == '__main__':

    build_parser ().parse_args (namespace = args)
    config = config_from_pyfile (args.profile)

    init_logging (
        args,
        logging.StreamHandler (),
        logging.FileHandler ('import.log')
    )

    parameters = dict ()

    dbdest = db_tools.PostgreSQLEngine (**config)

    log (logging.INFO, "Creating Database Schema ...")

    # db.Base.metadata.drop_all  (dbdest.engine)
    # db.Base2.metadata.drop_all (dbdest.engine)
    # db.Base4.metadata.drop_all (dbdest.engine)

    db.Base.metadata.create_all  (dbdest.engine)
    db.Base2.metadata.create_all (dbdest.engine)
    db.Base4.metadata.create_all (dbdest.engine)

    log (logging.INFO, "Done")
