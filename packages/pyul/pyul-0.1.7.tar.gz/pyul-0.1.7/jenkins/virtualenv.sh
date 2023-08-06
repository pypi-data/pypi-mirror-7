#!/bin/bash
# Check to see if pip and virtualenv is installed
hash pip 2>/dev/null || { echo >&2 "I require foo but it's not installed.  Aborting."; exit 1; }

hash pip 2>/dev/null || { echo >&2 "Unable to find pip.  Aborting."; exit 1; }
hash virtualenv 2>/dev/null || { echo >&2 "Unable to find virtualenv.  Aborting."; exit 1; }

venv_name=.virtualenv
virtualenv_activate=./${venv_name}/bin/activate

# Validate the virtualenv and activate it
virtualenv $venv_name
. ${virtualenv_activate}

if [[ "$1" == "install" ]]
then
  pip install --upgrade pyul
else
  python setup.py develop
fi
