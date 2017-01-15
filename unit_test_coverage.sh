#!/usr/bin/env bash
# we need the repo for coveralls' reports
# clone into a new folder, as git will not allow the current folder as it is not empty
git clone https://github.com/bahrmichael/aws-python-stack repo
mv repo/.git .
rm -Rf repo
coverage run -m unittest discover
COVERALLS_REPO_TOKEN=$TOKEN coveralls