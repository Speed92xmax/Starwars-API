rm -R -f ./migrations &&
pipenv run init &&
pipenv run migrate &&
pipenv run upgrade
