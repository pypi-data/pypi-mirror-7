if [[ "${RELEASE_TYPE}" == "" ]]
then 
  RELEASE_TYPE=patch
fi
if [[ "${PYPI_NAME}" == "" ]]
then 
  PYPI_NAME=rocktaviouspypi
fi

python setup.py tag --${RELEASE_TYPE} register -r ${PYPI_NAME} sdist bdist_egg bdist_wheel upload -r ${PYPI_NAME}