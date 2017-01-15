#!/usr/bin/env bash
# clone into a new folder, as git will not allow the current folder as it is not empty
git clone https://github.com/bahrmichael/aws-python-stack repo
cd repo/tests/unit
coverage run -m unittest discover
COVERALLS_REPO_TOKEN=$TOKEN coveralls