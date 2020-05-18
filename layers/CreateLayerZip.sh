#!/bin/bash
PY_DIR='build/python/lib/python3.8/site-packages'
mkdir -p $PY_DIR                                              #Create temporary build directory
pipenv lock -r > requirements.txt                             #Generate requirements file
pip install -r requirements.txt -t $PY_DIR     #Install packages into the target directory
cd build
zip -r ../../ZipFiles/$1.zip .                                  #Zip files
cd ..
rm -r build 
