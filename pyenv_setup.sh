#!/usr/bin/env sh
for version in $(cat .python-version)
do
    pyenv install $version
done

pyenv local $(cat .python-version)