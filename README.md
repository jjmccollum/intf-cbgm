# Projektbeschreibung

- Umsetzung der CBGM (Coherence-Based Genealogical Method) auf
  Datenbankebene.

- Entwicklung eines Web-Frontends für die Zielgruppen: Editoren der ECM,
  Philologen, interessierte Laien. Ermöglicht eine visuelle Exploration
  der Datenbasis des ECM.

- Fernziel: Interaktivität auch für externe Nutzer.

Website: http://ntg.uni-muenster.de/

Dokumentation unter: https://cceh.github.io/ntg/

# Installation mit Docker

## Voraussetzungen

- Docker
- Docker-Compose
- npm

npm installieren unter Debian/Ubuntu:

    curl -sL https://deb.nodesource.com/setup_14.x | sudo -E bash -
    sudo apt-get install -y nodejs

Getestet mit Node v14.15.0 sowie npm v6.14.8 (kein yarn!)

## Hinweis

In der `package.json` muss explizit `"bootstrap-vue": "2.17.0"` angegeben sein.  
Alle Versionen 2.17+ sind breaking, da sie nicht mehr "utils/key-codes" enthalten.

## Schritt-für-Schritt Anleitung

1. Node Modules für Webpack holen: `cd client` und `npm install`.
2. Makefile ausführen `cd ../docker` sowie `make`.
3. Das Makefile in Docker ruft u.a. ein weiteres Makefile unter client auf.
4. Wenn keine Fehler auftraten mit `docker-compose up` starten. Beim ersten Aufruf wird Postgres den Dump einspielen.
5. Beim zweiten Start `docker-compose run` nutzen

## Direkter Zugriff auf Postgres

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

## Änderung des Datengrundlage für Docker

1. Ein passenden Dump unter `docker/backup` ablegen. Der genaue Aufbau muss aus den bisherigen Dumps erschlossen werden.
2. Unter `docker/docker-entrypoint-initdb.d` in allen Dateien den Datenbanknamen anpassen, etwa "acts_ph4"
3. Unter `docker/docker-entrypoint.sh` die Config an den Datenbanknamen anpassen
4. Unter `docker` deine passende .conf erstellen. Am besten an bestender Datei orientieren.

Unter dem Punkt "Backup" in `docker/Makefile` muss ggf. auch der Datenbankname angepasst werden.

# Roadmap

- Bisher wird der Postgres Dump in Gitlab abgelegt -> Datenrepository nutzen
- Bisher werden die Images lokal gebaut -> Gitlab Registry nutzen
