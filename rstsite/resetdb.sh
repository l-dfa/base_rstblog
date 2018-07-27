#!/bin/bash

#set BASE_DIR="C:/Dati/Studio/Sviluppi/base_rstblog/rstsite"
rem BASE_DIR=/usr/share/nginx/html/ldfa/rstsite

rm -f db.sqlite3
rm -fv $BASE_DIR/rstblog/migrations/0*

python manage.py makemigrations rstblog

python manage.py migrate

python mkinitdb.py
