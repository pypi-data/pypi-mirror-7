#!/bin/sh
python setup.py clean
echo "Cleaning .pyc files"
find . -type f -name "*.pyc" -print0 | xargs -r -0 rm
echo "Running PEP8 checks"
flake8 --max-complexity 23 --exclude=ClientInterface
if [ $? -ne 0 ]
then
    echo "pyflake8 errors detected. Stopping run."
    exit 1
fi

nosetests
if [ $? -ne 0 ]
then
    echo "nosetests failed. Stopping run."
    exit 1
fi
echo "nosetests passed"
