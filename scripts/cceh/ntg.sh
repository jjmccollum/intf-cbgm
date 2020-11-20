#!/bin/bash

# read -p "Enter Name of Book (e.g. Mark): "  BOOK
# read -p "Enter Version # of Phase (e.g. 2.3): "  PHASE

# sed -i 's/doch/ach/' test.cfg

BOOK="Mark"
PHASE="3.2"
SHORTCUT="Mg"

# Build filename for config
LOWER=`echo ${BOOK} | awk '{print tolower($0)}'`
VERSION=`echo ${PHASE//.}`
FILENAME=`echo ${LOWER}_ph${VERSION}.conf`

# echo 'Hello World' > $FILENAME

mv $FILENAME ${FILENAME}_old

cat <<EOT>> $FILENAME
APPLICATION_NAME="${BOOK} Phase ${PHASE}"
APPLICATION_ROOT="${LOWER}/ph${VERSION}/"

BOOK="${BOOK}"

READ_ACCESS="editor"
READ_ACCESS_PRIVATE="editor"
WRITE_ACCESS="editor_${LOWER}"

PGHOST="localhost"
PGPORT="5432"
PGDATABASE="${LOWER}_ph${VERSION}"
PGUSER="ntg"

# MYSQL

MYSQL_CONF="~/.my.cnf"
MYSQL_GROUP="mysql"

MYSQL_ECM_DB="ECM_${BOOK}_Ph${VERSION}"
MYSQL_ATT_TABLES="${SHORTCUT}\d+"
MYSQL_LAC_TABLES="${SHORTCUT}\d+lac"
MYSQL_VG_DB="ECM_${BOOK}_Ph${VERSION}"

MYSQL_NESTLE_DB="Nestle29"
MYSQL_NESTLE_TABLE="Nestle29"
EOT