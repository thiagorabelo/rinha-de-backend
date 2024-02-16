#!/bin/sh

echo "\"galo\" \"$(psql -Atqc "SELECT rolpassword FROM pg_authid WHERE rolname = 'galo';")\"" > /pgbouncer/userlist/userlist.txt
