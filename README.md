# Genealogical Queries

## A Tool for the Coherence-Based Genealogical Method

<div style="text-align: center;"><a href="http://egora.uni-muenster.de/intf/">
<img src="https://ntg.uni-muenster.de/images/intf-logo.png" width="150"/></a> <a href="https://www.uni-muenster.de/SCDH/"><img src="https://www.uni-muenster.de/imperia/md/images/SCDH/_v/logo.svg" style="margin: 2rem; vertical-align: top" width="150"/> </a>
</div>
---

## Kontext

"Genealogical Queries" ist eine Sammlung von Tools, um die CBGM anzuwenden. Sie besteht aus einer Vue-basierten Oberfläche, einem Flask-basiertem Backend, einer Postgres Datenbank, vielen Python Skripten und weiteren 3rd-Party-Tools und Bibliotheken.

- [Was ist die Coherence-Based Genealogical Method?](https://www.uni-muenster.de/INTF/Genealogical_method.html)
- [Wie funktioniert das Genealogical Queries Tool?](https://ntg.uni-muenster.de/pdfs/GenQ4_Guide.pdf)
- [Wo wird die CBGM eingesetzt?](https://en.wikipedia.org/wiki/Editio_Critica_Maior)

## Weitere Links

Live-Server: http://ntg.uni-muenster.de/

Dokumentation unter: https://scdh.github.io/ntg/

# Installation

Derzeit ist es möglich, das Tool auf einem Server zu betreiben.  
Deutlich einfacher jedoch ist es, das Tool über Docker zu starten.

# Installation mit Docker

**Aktuelles Datenmodell**: Acts Phase 4 / Apostelgeschichte (4.Phase)

## Anleitung Docker

1. Installieren Sie [Docker](https://www.docker.com/get-started) sowie ggf. docker-compose (unter Linux/Mac).
2. Speichern Sie die Datei [docker-compose.yml](https://raw.githubusercontent.com/SCDH/ntg/master/docker/docker-compose.yml) in einem Ordner ihrer Wahl.
3. Führen Sie dort den Befehl `docker-compose up` aus
4. Rufen Sie in Ihrem Browser die Adresse `http://localhost:5000` auf
5. Beenden Sie das Tool per `docker-compose stop`, beim nächsten Start `docker-compose start`

Hinweis: Alle Docker Images finden Sie unter  
[hub.docker.com | intf-cbgm-app-server](https://hub.docker.com/r/scdh/intf-cbgm-app-server)  
[hub.docker.com | intf-cbgm-db-server](https://hub.docker.com/r/scdh/intf-cbgm-db-server)

---

## Schritt-für-Schritt Anleitung (nur für Entwickler)

### Voraussetzungen

- Docker
- Docker-Compose
- npm 6.x

npm installieren unter Debian/Ubuntu:

    curl -sL https://deb.nodesource.com/setup_14.x | sudo -E bash -
    sudo apt-get install -y nodejs

Getestet mit Node v14.15.0 sowie npm v6.14.8.  
Nicht mit yarn getestet.

Hinweis: In der `package.json` muss explizit `"bootstrap-vue": "2.17.0"` angegeben sein.  
Alle Versionen 2.17+ sind breaking, da sie nicht mehr "utils/key-codes" enthalten.

1. Node Modules für Webpack holen: `cd client` und `npm install`.
2. Makefile ausführen `cd ../docker` sowie `make`.
3. Das Makefile in Docker ruft u.a. ein weiteres Makefile unter client auf.
4. Wenn keine Fehler auftraten mit `docker-compose up` starten. Beim ersten Aufruf wird Postgres den Dump einspielen.
5. Beim zweiten Start `docker-compose run` nutzen

### Direkter Zugriff auf Postgres

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

einen SUPERUSER anzulegen. Dann mit DataGrip oder einer anderen Anwendung auf `postgresql://localhost:5432/acts_ph4` verbinden

### Änderung der Datengrundlage für Docker

Z.B. um von Acts Phase 4 auf eine andere Phase zu wechseln.

1. Ein passenden Dump unter `docker/backup` ablegen. Der genaue Aufbau muss aus den bisherigen Dumps erschlossen werden.
2. Unter `/docker/docker-entrypoint-initdb.d` in allen Dateien den Datenbanknamen anpassen, etwa "acts_ph4"
3. Unter `/docker/docker-entrypoint.sh` die Config an den Datenbanknamen anpassen
4. Unter `/docker` die passende .conf erstellen. Am besten an bestender Datei orientieren.

Unter dem Punkt "Backup" in `docker/Makefile` muss ggf. auch der Datenbankname angepasst werden.
