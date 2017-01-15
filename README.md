# AWS Python Stack

This project is a skeleton for aws **lambda** functions which are written in Python. Note that aws lambda currently only 
supports Python 2.7 module, but the function code can be written in Python 3.5.

**WARNING**: This repo has quite a lot of open todos. AS Lambda deployment is not yet explained. 
If you find this interesting, please star or fork and leave comments/issues for whatever you would like to see.

## TODO

* Add environment settings and triggers to function's readme
* Add aws requirements to requirements section
* Explain zappa_settings.json files
* Explain deployment with zappa
* Setup integration testing

## Requirements

* Python 3.5 (and 2.7 for the aws functions) and pip
* The requirements from `requirements-dev.txt`
* virtualenv (to create virtual environments per function)
* Docker >= 1.12
* Coveralls account
* Codeship account
* Jet from codeship (optional) to run codeship builds locally

## Setup

* Fork this repo
* Update `unit_test_coverage.sh` to match your repo
* Add a project to codeship for this repo
* Download the `codeship.aes` and add it to your `.gitignore`
* [Encrypt environment variables](https://documentation.codeship.com/pro/getting-started/encryption/) and commit the encrypted files (not the decrypted ones!)
    * coveralls.env: TOKEN=YOUR_COVERALLS_TOKEN -> coveralls.env.encrypted

## Run

* `jet steps`
* `jet steps --tag master` to add coverage reporting