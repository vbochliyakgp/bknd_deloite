#!/bin/bash

# create the database
createdb -U postgres vibemeter

# create the tables
psql -U postgres -d vibemeter -f "$(dirname "$(realpath "$0")")/create_tables.sql"