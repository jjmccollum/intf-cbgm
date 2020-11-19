# -*- coding: utf-8 -*-
import os
import fileinput

"""
This file is part of the CBGM Project @ INTF - WWU Münster

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
    "book": "",
    "phase": "",
    "shortcut": ""
}
global bcolors
bcolors = {
    "HEADER":'\033[95m',
    "OKBLUE":'\033[94m',
    "OKCYAN":'\033[96m',
    "OKGREEN":'\033[92m',
    "WARNING":'\033[93m',
    "ERROR":'\033[91m',
    "ENDC":'\033[0m'}

def is_number(s):
    """
    helper function
    """
    try:
        float(s)
        return True
    except ValueError:
        return False

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
    write_db_config(project_data)
    user_input = 'n'
    user_input = input(
        f'{bcolors["OKBLUE"]}> Set database of preceding phase to READ ONLY? (y/n): {bcolors["ENDC"]}')
    if (user_input == 'y'):
        set_write_access(project_data)
    activate_db(project_data)
    return project_data


def get_inputs(project_data):
    """
    Asks the user for necessary informations
    """
    while (project_data['book'] == ''):
        project_data['book'] = input(f'{bcolors["OKBLUE"]}> Name of Book (e.g. Mark)?: {bcolors["ENDC"]}')
    while (project_data['phase'] == ''):
        project_data['phase'] = input(f'{bcolors["OKBLUE"]}> Name of Phase (e.g. 3.2)?: {bcolors["ENDC"]}')
        if not is_number(project_data['phase']):
            print(f'{bcolors["ERROR"]}ERROR: Could not parse Phase information. Is it a valid number?{bcolors["ENDC"]}')
            project_data['phase'] = ''
    while (project_data['shortcut'] == ''):
        project_data['shortcut'] = input(f'{bcolors["OKBLUE"]}> Name of Shortcut (e.g. Mk)?: {bcolors["ENDC"]}')

    # generate additional project data
    project_data['book_l'] = project_data['book'].lower()
    project_data['version'] = project_data['phase'].replace('.', '')
    project_data['book_and_phase'] = project_data['book_l'] + '_ph' + project_data['version']
    project_data['config_file'] = project_data['book_and_phase'] + '.conf'

    return project_data


def set_write_access(project_data):
    """
    sets the write access for preceding(!) phase in db config file to "nobody"
    """

    # calculate preceding phase number
    preceding_version = project_data['version']
    try:
        preceding_version = (int(project_data['version']))-1
        if preceding_version < 10:
            preceding_version = "0." + str(preceding_version)
        else:
            preceding_version = (str(preceding_version)[0] + '.' + str(preceding_version)[1])

    except Exception as e:
        print(f'{bcolors["ERROR"]}ERROR: Could not parse Phase information. Is it a valid number?{bcolors["ENDC"]}')
        print(e)

    preceding_book = project_data['book']
    pre_phase_correct = 'n' # set to "no"
    pre_phase_correct = input(
        f'{bcolors["OKBLUE"]}> Is "{preceding_book} {preceding_version}" the correct name for the preceding phase? (y/n): {bcolors["ENDC"]}')
    if (pre_phase_correct == 'y'):
        preceding_book_l = preceding_book.lower()
        preceding_config = preceding_book_l + '_ph' + str(preceding_version).replace('.','')  + '.conf'
    else:
        pre_phase = input(
            f'{bcolors["OKBLUE"]}> Please enter the name of the preceding phase (e.g. "Mark 2.3"): {bcolors["ENDC"]}')
        tmp = pre_phase.split(' ')
        preceding_config = tmp[0].lower() + '_ph' + tmp[1].replace('.','') + '.conf'
        preceding_book_l = tmp[0].lower()
    project_data['preceding_book_l'] = preceding_book_l
    project_data['preceding_config'] = preceding_config

    # set write access in file of preceding phase
    try:
        config_file = project_data['preceding_config']
        wa_string = 'WRITE_ACCESS="editor_' + project_data['preceding_book_l'] + '"'
        for line in fileinput.input([config_file], inplace=True):
            print(line.replace(wa_string,'WRITE_ACCESS="nobody"'),end='')
    except Exception as e:
        print(f'{bcolors["ERROR"]}ERROR: While trying to set write access. Does {config_file} exists?{bcolors["ENDC"]}')
        print(e)
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

    with open(project_data['config_file'], "w") as w:
        w.write(configuration.format(project_data['book'], project_data['phase'],
                                     project_data['book_l'], project_data['version'], project_data['shortcut']))


def activate_db(project_data):
    """
    adds the new phase/project to the file active_databases
    """
    print('Adding Database to Active Databases.')
    book_and_phase = project_data['book_and_phase']
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
        print(f'{bcolors["ERROR"]}ERROR: While writing to active_databases.{bcolors["ENDC"]}')
        print(e)


# main entry point for this script
print(ascii_art)
choice = input(
    f'PLEASE SELECT:\n(0) Starting a New Phase With Apparatus Update\n(1) Starting a New Project\n{bcolors["OKBLUE"]}> (Default = 0): {bcolors["ENDC"]}')

if choice == '1':
    new_project(project_data)
else:
    new_phase(project_data)

# os.system('ls -l')
# os.system('python -m script')
