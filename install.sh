#!/bin/bash

usage () {
    echo "A clean virtual environment with python3 as python default must be activated before installation"
    exit $0
    }

#
#   MAIN
#

# check if you already are in a virtual environment with python 3 as default python, in the other cases exit
python -c "import sys ; sys.exit(0 if (hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)) else 1)"
if [ $? -ne 0 ]; then
    usage 1
fi

py_maj_ver="$(python -c "import sys ; print(sys.version_info.major)")"

if [ "$py_maj_ver" != "3" ]; then
    usage 1
fi

if [ -f db.sqlite3 ]; then
    echo "db.sqlite3 file already exists, please remove it and run again the script"
    exit 2
fi

pip install -r requirements.txt

python ./manage.py makemigrations pycsw4django
python ./manage.py migrate
python ./manage.py runserver
