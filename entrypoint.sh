#!/bin/bash
# cd sparkWorkshop/

python3 manage.py migrate
python3 manage.py collectstatic --noinput
python3 manage.py createcachetable

supervisord