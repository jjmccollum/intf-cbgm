#!/bin/bash

pg_restore -U postgres --dbname=mark_ph31 -n ntg --verbose --single-transaction < backup/mark_ph31.dump
