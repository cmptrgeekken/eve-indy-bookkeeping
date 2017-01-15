#!/usr/bin/env bash
# clone into a new folder, as git will not allow the current folder as it is not empty
git clone https://github.com/<USER>/<REPO> <FOLDER>
cd <FOLDER>
coverage run -m unittest discover
COVERALLS_REPO_TOKEN=$TOKEN coveralls