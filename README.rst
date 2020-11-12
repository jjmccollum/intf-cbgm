.. -*- encoding: utf-8; bidi-paragraph-direction: left-to-right; fill-column: 72 -*-

Projektbeschreibung
===================

- Umsetzung der CBGM (Coherence-Based Genealogical Method) auf
  Datenbankebene.

- Entwicklung eines Web-Frontends für die Zielgruppen: Editoren der ECM,
  Philologen, interessierte Laien.  Ermöglicht eine visuelle Exploration
  der Datenbasis des ECM.

- Fernziel: Interaktivität auch für externe Nutzer.

Website:  http://ntg.uni-muenster.de/

Dokumentation unter: https://cceh.github.io/ntg/

Docker Installation
===================

Voraussetzungen:

* Docker
* Docker-Compose
* NPM

NPM installieren unter Debian/Ubuntu:

    curl -sL https://deb.nodesource.com/setup_14.x | sudo -E bash -
    sudo apt-get install -y nodejs

Getestet mit Node v14.15.0 sowie NPM v6.14.8 (kein yarn!)

Wichtig:

In der `package.json` muss explizit `"bootstrap-vue": "2.17.0"` angegeben sein.  
Alle Versionen 2.17+ sind breaking, da sie nicht mehr "utils/key-codes" enthalten.

Installationsanleitung:

1. Node Modules für Webpack holen: `cd client` und `npm install`.
2. Makefile ausführen `cd ../docker` sowie `make`.
3. Das Makefile in Docker ruft u.a. ein weiteres Makefile unter client auf.
4. Wenn keine Fehler auftraten mit `docker-compose up` starten. Beim ersten Aufruf wird Postgres den Dump einspielen.
5. Beim zweiten Start `docker-compose run` nutzen

Direkter Zugriff auf Postgres:

Um direkt auf Postgres innerhalb des Containers "ntg-db-server" zuzugreifen, muss der Port nach außen geöffnet werden.
In `docker-compose.yml` expose und ports hinzufügen:

    services:
      ntg-db-server:
        image: intf/ntg-db-server
        volumes:
          - pgdata:/var/lib/postgresql
        expose:
          - 5432
        ports:
          - 5432:5432

Am einfachsten ist es, sich über 

    docker exec -it <container-id> bash

einzuloggen und mit

    su postgres
    psql
    CREATE USER myUserName WITH PASSWORD 'topsecret'
    ALTER USER myUserName WITH SUPERUSER;

einen SUPERUSER anzulegen. Dann mit DataGrip oder einer anderen Anwendung auf `postgresql://localhost:5432/mark_ph31` verbinden

ToDos:

* Bisher wird der Postgres Dump in Gitlab abgelegt -> Datenrepository nutzen
* Bisher werden die Images lokal gebaut -> Gitlab Registry nutzen
