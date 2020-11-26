# Genealogical Queries

## A Tool for the Coherence-Based Genealogical Method

<div style="text-align: center;"><a href="http://egora.uni-muenster.de/intf/">
<img src="https://ntg.uni-muenster.de/images/intf-logo.png" width="150"/></a> <a href="https://www.uni-muenster.de/SCDH/"><img src="https://www.uni-muenster.de/imperia/md/images/SCDH/_v/logo.svg" style="margin: 2rem; vertical-align: top" width="150"/> </a>
</div>

---

"Genealogical Queries" is a collection of tools to apply the CBGM. It consists of a Vue-based interface, a Flask-based backend, a postgres database, many Python scripts and other 3rd party tools and libraries.

- What is the Coherence-Based Genealogical Method?](https://www.uni-muenster.de/INTF/Genealogical_method.html)
- How does the Genealogical Queries Tool work?](https://ntg.uni-muenster.de/pdfs/GenQ4_Guide.pdf)
- Where is the CBGM used?](https://en.wikipedia.org/wiki/Editio_Critica_Maior)

## Other links

Live server: http://ntg.uni-muenster.de/

Documentation at: https://scdh.github.io/intf-cbgm/

# Installation

Currently it is possible to run "Genealogical Queries" on a self-hosted server.  
But it is much easier to start via Docker.

# Installation with Docker

**Current data model**: Acts Phase 4 / Acts of the Apostles (4th phase)

## Instructions Docker

1. Install [Docker](https://www.docker.com/get-started) and if necessary docker-compose (under Linux/Mac)
2. Save the file [docker-compose.yml](https://raw.githubusercontent.com/SCDH/ntg/master/docker/docker-compose.yml) in a folder of your choice
3. Execute the command [docker-compose up
4. Call up the address `http://localhost:5000` in your browser
5. Quit "Genealogical Queries" via `docker-compose stop`, at the next start `docker-compose run`

Note: All Docker Images can be found at  
[hub.docker.com | intf-cbgm-app-server](https://hub.docker.com/r/scdh/intf-cbgm-app-server)  
[hub.docker.com | intf-cbgm-db-server](https://hub.docker.com/r/scdh/intf-cbgm-db-server)

---

## Step-by-step guide (for developers only)

### Requirements

- Docker
- Docker-Compose
- npm 6.x

Install npm under Debian/Ubuntu:

    curl -sL https://deb.nodesource.com/setup_14.x | sudo -E bash -
    sudo apt-get install -y nodejs

Tested with Node v14.15.0 and npm v6.14.8.  
Not tested with yarn.

Note: The `package.json` must explicitly state `"bootstrap-vue": "2.17.0"`.  
All versions 2.17+ are breaking because they do not contain "utils/key-codes" anymore.

1. Get node modules for webpack: `cd client` and `npm install`.
2. Execute Makefile: `cd ../docker` and `make`.
3. The Makefile in Docker calls another Makefile under client
4. If no errors occurred start with `docker-compose up`. At the first call Postgres will import the dump.
5. Use `docker-compose run` on the second start

### Direct access to postgres

To access postgres inside the container "ntg-db-server" directly, the port must be open.
In `docker-compose.yml` add expose and ports:

    services:
      ntg-db-server:
        image: intf/ntg-db-server
        volumes:
          - pgdata:/var/lib/postgresql
        expose:
          - 5432
        ports:
          - 5432:5432

The easiest way to do this is

    docker exec -it <container-id> bash

and do

    su postgres
    psql
    CREATE USER myUserName WITH PASSWORD 'topsecret'
    OLD USER myUserName WITH SUPERUSER;

to create a SUPERUSER. Then connect via DataGrip or any another application to `postgresql://localhost:5432/acts_ph4`

### Change the data in docker container

For example, to switch from Acts Phase 4 to another phase, do the following:

1. Place a suitable dump under `docker/backup`. The exact structure is quite complex and knowledge of the NTVMR (New Testament Virtual Manuscript Room) ist necessary. Feel free to [contact us](mailto:dennis.voltz@wwu.de) for help.
2. Adjust the database name under `/docker/docker-entrypoint-initdb.d` in all files, for example "acts_ph4"
3. Adapt the config to the database name under `/docker/docker-entrypoint.sh`
4. Create the appropriate .conf under `/docker`. The best way to do this is to copy the existing file.

Note: In property "backup" in `docker/Makefile` you may also have to adjust the database name.
