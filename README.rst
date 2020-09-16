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

Getting Started:

1. cd docker 
2. make run

ToDos:

* Bisher wird der Postgres Dump in Gitlab abgelegt -> Datenrepository nutzen
* Bisher werden die Images lokal gebaut -> Gitlab Registry nutzen
