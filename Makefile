RSYNC   := /usr/bin/rsync -azv --exclude '*~'
SHELL   := /bin/bash
PYTHON  := /usr/bin/python3
BROWSER := firefox

NTG_VM	   := ntg.cceh.uni-koeln.de
NTG_USER   := ntg
NTG_DB     := ntg
NTG        := $(NTG_USER)@$(NTG_VM)
NTG_ROOT   := $(NTG):/home/$(NTG_USER)/prj/ntg/ntg
PSQL_PORT  := 5433
SERVER     := server
STATIC	   := $(SERVER)/static

TRANSLATIONS := de			 # space-separated list of translations we have eg. de fr

NTG_SERVER := $(NTG_ROOT)/$(SERVER)
NTG_STATIC := $(NTG_ROOT)/$(STATIC)

LESS	   := $(wildcard $(STATIC)/css/*.less)
CSS		   := $(LESS:.less=.css)
CSS_GZ	   := $(patsubst %, %.gzip, $(CSS))

JS		   := $(STATIC)/js/*.js
JS_GZ	   := $(patsubst %, %.gzip, $(JS))

PY_SOURCES := scripts/cceh/*.py ntg_common/*.py server/*.py

.PHONY: upload upload_po update_pot update_po update_mo update_libs vpn server restart psql
.PHONY: js css jsdoc lint pylint jslint csslint

restart: js css server

server: css js
	server/server.py -vv

prepare:
	scripts/cceh/prepare4cbgm.py -vvv server/instance/current.conf

users:
	scripts/cceh/mk_users.py -vvv server/instance/_global.conf

db_upload:
	pg_dump --clean --if-exists ntg_current | bzip2 > /tmp/ntg_current.pg_dump.sql.bz2
	scp /tmp/ntg_current.pg_dump.sql.bz2 $(NTG_USER)@$(NTG_VM):~/

clean:
	find . -depth -name "*~" -delete

psql:
	ssh -f -L 1$(PSQL_PORT):localhost:$(PSQL_PORT) $(NTG_USER)@$(NTG_VM) sleep 120
	sleep 1
	psql -h localhost -p 1$(PSQL_PORT) -d $(NTG_DB) -U $(NTG_USER)


lint: pylint jslint csslint

pylint:
	-pylint $(PY_SOURCES)

jslint:
	./node_modules/.bin/eslint -f unix Gruntfile.js $(JS)

csslint: css
	csslint --ignore="adjoining-classes,box-sizing,ids,order-alphabetical,overqualified-elements,qualified-headings" $(CSS)

jsdoc:
	jsdoc -d jsdoc -a all $(JS) && $(BROWSER) jsdoc/index.html

bower_update:
	bower install --update

upload:
	$(RSYNC) --exclude "**/__pycache__"  --exclude "*.pyc"  ntg_common $(NTG_ROOT)/
	$(RSYNC) --exclude "**/instance/**"       server     $(NTG_ROOT)/

css: $(CSS)

js:	$(JS)

%.css : %.less
	lessc --autoprefix="last 2 versions" $? $@

%.gzip : %
	gzip < $? > $@

install-prerequisites:
	sudo apt-get install libpq-dev postgresql-9.6-python3-multicorn graphviz
	pip3 install numpy six networkx matplotlib Pillow rtree
	pip3 install psycopg2 mysqlclient sqlalchemy sqlalchemy-utils intervals multicorn
	pip3 install flask babel flask-babel flask-sqlalchemy jinja2 flask-user

### Localization ###

define LOCALE_TEMPLATE

.PRECIOUS: po/$(1).po

update_mo: server/translations/$(1)/LC_MESSAGES/messages.mo

update_po: po/$(1).po

po/$(1).po: po/server.pot
	if test -e $$@; \
	then msgmerge -U --backup=numbered $$@ $$?; \
	else msginit --locale=$(1) -i $$? -o $$@; \
	fi

server/translations/$(1)/LC_MESSAGES/messages.mo: po/$(1).po
	-mkdir -p $$(dir $$@)
	msgfmt -o $$@ $$?

endef

$(foreach lang,$(TRANSLATIONS),$(eval $(call LOCALE_TEMPLATE,$(lang))))

po/server.pot: $(PY_SOURCES) $(TEMPLATES) pybabel.cfg Makefile
	PYTHONPATH=.; pybabel extract -F pybabel.cfg --no-wrap --add-comments=NOTE \
	--copyright-holder="CCeH Cologne" --project=NTG --version=2.0 \
	--msgid-bugs-address=marcello@perathoner.de \
	-k 'l_' -k 'n_:1,2' -o $@ .

update_pot: po/server.pot
