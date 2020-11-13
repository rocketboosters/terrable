# Terrable

[![PyPI version](https://badge.fury.io/py/terrable.svg)](https://pypi.org/project/terrable/)
[![build status](https://gitlab.com/rocket-boosters/terrable/badges/main/pipeline.svg)](https://gitlab.com/rocket-boosters/terrable/commits/main)
[![coverage report](https://gitlab.com/rocket-boosters/terrable/badges/main/coverage.svg)](https://gitlab.com/rocket-boosters/terrable/commits/main)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Code style: flake8](https://img.shields.io/badge/code%20style-flake8-white)](https://gitlab.com/pycqa/flake8)
[![Code style: mypy](https://img.shields.io/badge/code%20style-mypy-white)](http://mypy-lang.org/)
[![PyPI - License](https://img.shields.io/pypi/l/terrable)](https://pypi.org/project/terrable/)

Terraform private module manager that uses S3 as a backend. Includes simple versioning
of modules to make forward migration easier. Terraform supports referencing modules
stored in S3 as compressed files (see
[S3 Bucket](https://www.terraform.io/docs/modules/sources.html#s3-bucket)
for more details). However, managing those packages is not part of Terraform itself.
That's where *terr&#8226;able* comes in. The terrable CLI allows for bundling terraform
module directories into compressed files and deploying them to S3 with simple
incremental versioning. That way modules changes can be gradually introduced in
dependent projects as needed without causing conflicts.

## Installation

Terrable is available via pip:

```shell script
$ pip install terrable
```

or via poetry:

```shell script
# poetry install terrable --dev
```

Once installed, the terrable CLI command will be available in your terminal.

## Usage

Terrable operates primarily on a directory that contains within it one or more module
directories. For example:

```
+---modules
|   \---aws-lambda-function
|           main.tf
|           output.tf
|           variables.tf
|           policy.json
|
|   \---aws-dynamo-db-table
|           main.tf
|           output.tf
|           variables.tf
```

Here the root "modules" folder contains two modules "aws-lambda-function"
and "aws-dynamo-db-table". To deploy these as modules via terrable to an S3 bucket
execute the command from the parent directory of the modules folder:

```shell script
$ terrable publish ./modules/ --bucket=<BUCKET_NAME> --profile=<AWS_PROFILE_NAME>
```

This command will iterate through each folder inside the modules directory and publish
any that have changed since their previous publish. Any modules found not to have
changed will be skipped. This can be overridden with the `--force` flag. It's also
possible to publish only specific modules within that folder by including the 
`--target=aws-lambda-function` flag. This flag can be specified multiple times to
publish a select number of specific modules for a given command.

To inspect modules, there is a list command:

```
$ terrable list <MODULE_NAME> --bucket=<BUCKET_NAME> --profile=<AWS_PROFILE_NAME>
```

This command will print all of the versions and associated metadata for the specified
module.
