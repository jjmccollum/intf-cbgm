import os
import fileinput

"""
This file is part of the CBGM Project @ INTF - WWU Münster
http://egora.uni-muenster.de/intf/

The CBGM is a method for inferring global manuscript stemmata 
from local stemmata in the manuscripts’ texts.
This software is free software; you can redistribute it and/or modify it
under the terms of the MIT License; see LICENSE file for more details.

Author: Dennis Voltz, SCDH @ WWU Münster
"""

# obligatory ascii art
ascii_art = """
 ██████╗██████╗  ██████╗ ███╗   ███╗
██╔════╝██╔══██╗██╔════╝ ████╗ ████║
██║     ██████╔╝██║  ███╗██╔████╔██║
██║     ██╔══██╗██║   ██║██║╚██╔╝██║
╚██████╗██████╔╝╚██████╔╝██║ ╚═╝ ██║
 ╚═════╝╚═════╝  ╚═════╝ ╚═╝     ╚═╝
"""

# variables
project_data = {
    "book": "Mark",
    "phase": "3.2",
    "shortcut": "Mk"
}


def new_project(project_data):
    """
    starts a new project
    """
    print('Starting a new project.')


def new_phase(project_data):
    """
    starts a new phase with apparatus update (default)
    currently, there is no new phase WITHOUT apparatus update
    """
    print('Starting a new phase.')
    get_inputs(project_data)
    return project_data


def get_inputs(project_data):
    """
    Asks the user for necessary informations
    """
    project_data['book'] = input("Name of Book (e.g. Mark)?: ")
    project_data['phase'] = input("Name of Phase (e.g. 3.2)?: ")
    project_data['shortcut'] = input("Name of Shortcut (e.g. Mk)?: ")

    return project_data

    # TODO calculate previous phase
    # pre_phase = 'Whatttt'

    # pre_phase_correct = input(
    #     f'Is "{pre_phase}" the correct name for the preceding phase? (y/n): ')
    # if (pre_phase_correct == 'y'):
    #     print('Great')
    # else:
    #     pre_phase = input(
    #         f'Please enter the name of the previous phase (e.g. "Mark 2.3"): ')


def set_write_access(project_data):
    """
    sets the write access for previous phase in db config file to "nobody"
    """
    # FIXME duplicate code!
    book = project_data['book'].lower()
    version = project_data['phase'].replace('.', '')
    book_and_phase = f'{book}_ph{version}'
    config_file = book_and_phase + '.conf'
    for line in fileinput.input([config_file], inplace=True):
        print(line.replace(f'WRITE_ACCESS="editor_{book}"',
                           'WRITE_ACCESS="nobody"'), end='')
    return None


def write_db_config(project_data):
    """
    writes the new db config file via template
    """
    configuration = """
    APPLICATION_NAME="{0} Phase {1}"
    APPLICATION_ROOT="{2}/ph{3}/"

    BOOK="{0}"

    READ_ACCESS="editor"
    READ_ACCESS_PRIVATE="editor"
    WRITE_ACCESS="editor_{2}"

    PGHOST="localhost"
    PGPORT="5432"
    PGDATABASE="{2}_ph{3}"
    PGUSER="ntg"

    # MYSQL

    MYSQL_CONF="~/.my.cnf"
    MYSQL_GROUP="mysql"

    MYSQL_ECM_DB="ECM_{0}_Ph{3}"
    MYSQL_ATT_TABLES="{4}\d+"
    MYSQL_LAC_TABLES="{4}\d+lac"
    MYSQL_VG_DB="ECM_{0}_Ph{3}"

    MYSQL_NESTLE_DB="Nestle29"
    MYSQL_NESTLE_TABLE="Nestle29"
    """

    book = project_data['book'].lower()
    version = project_data['phase'].replace('.', '')
    book_and_phase = f'{book}_ph{version}'
    config_file = book_and_phase + '.conf'
    with open(config_file, "w") as w:
        w.write(configuration.format(book, project_data['phase'],
                                     book.lower(), version, project_data['shortcut']))


def activate_db(project_data):
    """
    adds the new phase/project to the file active_databases
    """
    print('Adding Database to Active Databases.')
    book = project_data['book'].lower()
    version = project_data['phase'].replace('.', '')
    book_and_phase = f'{book}_ph{version}'
    try:
        with open("active_databases", "r") as f:
            for line in f:
                line_list = line.split('=')
                db_string = line_list[1].replace('"', '').strip()
                db_list = db_string.split(' ')
                last_elem = (db_list[len(db_list)-1])
                if last_elem != book_and_phase:
                    db_list.append(book_and_phase)
                    new_db_string = ' '.join(db_list)
                    new_line = 'ACTIVE_DATABASES="' + new_db_string + '"'
                    with open("active_databases", "w") as w:
                        w.write(new_line)
                    print('Successfully added.')
                else:
                    print('Database already marked as active.')
                break  # end after first line
    except Exception as e:
        print('Error while writing to active_databases.')
        print(e)


# main entry point for this script
print(ascii_art)
choice = input(
    "PLEASE SELECT:\n(0) Starting a New Phase With Apparatus Update\n(1) Starting a New Project\n(Default = 0): ")

if choice == '1':
    new_project(project_data)
else:
    new_phase(project_data)

# os.system('ls -l')
# os.system('python -m script')
