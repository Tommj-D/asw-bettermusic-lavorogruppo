#!/bin/sh
set -eu

psql -v ON_ERROR_STOP=1 \
    --username "$POSTGRES_USER" \
    --dbname "$POSTGRES_DB" \
    -v album_user="${ALBUM_DB_USER:-album_user}" \
    -v album_pass="${ALBUM_DB_PASSWORD:-$POSTGRES_PASSWORD}" \
    -v recensioni_user="${RECENSIONI_DB_USER:-recensioni_user}" \
    -v recensioni_pass="${RECENSIONI_DB_PASSWORD:-$POSTGRES_PASSWORD}" \
    -v connessioni_user="${CONNESSIONI_DB_USER:-connessioni_user}" \
    -v connessioni_pass="${CONNESSIONI_DB_PASSWORD:-$POSTGRES_PASSWORD}" \
    -v seguite_user="${SEGUITE_DB_USER:-seguite_user}" \
    -v seguite_pass="${SEGUITE_DB_PASSWORD:-$POSTGRES_PASSWORD}" <<-'EOSQL'
CREATE USER :"album_user" WITH PASSWORD :'album_pass';
CREATE DATABASE album_db OWNER :"album_user";
REVOKE ALL ON DATABASE album_db FROM PUBLIC;

CREATE USER :"recensioni_user" WITH PASSWORD :'recensioni_pass';
CREATE DATABASE recensioni_db OWNER :"recensioni_user";
REVOKE ALL ON DATABASE recensioni_db FROM PUBLIC;

CREATE USER :"connessioni_user" WITH PASSWORD :'connessioni_pass';
CREATE DATABASE connessioni_db OWNER :"connessioni_user";
REVOKE ALL ON DATABASE connessioni_db FROM PUBLIC;

CREATE USER :"seguite_user" WITH PASSWORD :'seguite_pass';
CREATE DATABASE recensioni_seguite_db OWNER :"seguite_user";
REVOKE ALL ON DATABASE recensioni_seguite_db FROM PUBLIC;
EOSQL
