# tap-holidays
[![PyPI version](https://badge.fury.io/py/tap-holidays.svg)](https://badge.fury.io/py/tap-holidays)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Python Versions](https://img.shields.io/badge/python-3.6%20%7C%203.7-blue.svg)](https://pypi.python.org/pypi/ansicolortags/)
[![Build Status](https://travis-ci.com/goodeggs/tap-holidays.svg?branch=master)](https://travis-ci.com/goodeggs/tap-holidays.svg?branch=master)

A [Singer](https://www.singer.io/) tap for extracting data from the [Holiday API](https://holidayapi.com/docs).

## Installation

Since package dependencies tend to conflict between various taps and targets, Singer [recommends](https://github.com/singer-io/getting-started/blob/master/docs/RUNNING_AND_DEVELOPING.md#running-singer-with-python) installing taps and targets into their own isolated virtual environments:

### Install Holidays Tap

```bash
$ python3 -m venv ~/.venvs/tap-holidays
$ source ~/.venvs/tap-holidays/bin/activate
$ pip3 install tap-holidays
$ deactivate
```

### Install Stitch Target (optional)

```bash
$ python3 -m venv ~/.venvs/target-stitch
$ source ~/.venvs/target-stitch/bin/activate
$ pip3 install target-stitch
$ deactivate
```

## Configuration

The tap accepts a JSON-formatted configuration file as arguments. This configuration file has a single required field:

1. `api_key`: A valid Holiday API key.

An bare-bones Holiday API configuration may file may look like the following:

```json
{
  "api_key": "foo"
}
```

### Granular Stream Configuration

Additionally, you may specify more granular configurations for individual streams. Each key under a stream should represent a valid API request parameter for that endpoint. A more fleshed-out configuration file may look similar to the following:

```json
{
  "api_key": "foo",
  "api_version": "v1",
  "streams": {
    "holidays": {
      "country": "US",
      "year": 2018,
      "subdivisions": true
    }
  }
}
```

## Streams

The current version of the tap syncs a single [Stream](https://github.com/singer-io/getting-started/blob/master/docs/SYNC_MODE.md#streams):
1. `Holidays`: [Endpoint Documentation](https://holidayapi.com/docs)

## Discovery

Singer taps describe the data that a stream supports via a [Discovery](https://github.com/singer-io/getting-started/blob/master/docs/DISCOVERY_MODE.md#discovery-mode) process. You can run the Dayforce tap in Discovery mode by passing the `--discover` flag at runtime:

```bash
$ ~/.venvs/tap-holidays/bin/tap-holidays --config=config/holidays.config.json --discover
```

The tap will generate a [Catalog](https://github.com/singer-io/getting-started/blob/master/docs/DISCOVERY_MODE.md#the-catalog) to stdout. To pass the Catalog to a file instead, simply redirect it to a file:s

```bash
$ ~/.venvs/tap-holidays/bin/tap-holidays --config=config/holidays.config.json --discover > catalog.json
```

## Sync to stdout

Running a tap in [Sync mode](https://github.com/singer-io/getting-started/blob/master/docs/SYNC_MODE.md#sync-mode) will extract data from the various selected Streams. In order to run a tap in Sync mode and have messages emitted to stdout, pass a valid configuration file and catalog file:

```bash
$ ~/.venvs/tap-holidays/bin/tap-holidays --config=config/holidays.config.json --catalog=catalog.json
```

The tap will emit occasional [Metric](https://github.com/singer-io/getting-started/blob/master/docs/SYNC_MODE.md#metric-messages), [Schema](https://github.com/singer-io/getting-started/blob/master/docs/SPEC.md#schema-message), [Record](https://github.com/singer-io/getting-started/blob/master/docs/SPEC.md#record-message), and [State messages](https://github.com/singer-io/getting-started/blob/master/docs/SPEC.md#state-message). You can persist State between runs by redirecting messages to a file:

```bash
$ ~/.venvs/tap-holidays/bin/tap-holidays --config=config/holidays.config.json --catalog=catalog.json >> state.json
$ tail -1 state.json > state.json.tmp
$ mv state.json.tmp state.json
```

## Sync to Stitch

You can also send the output of the tap to [Stitch Data](https://www.stitchdata.com/) for loading into the data warehouse. To do this, first create a JSON-formatted configuration for Stitch. This configuration file has two required fields:
1. `client_id`: The ID associated with the Stitch Data account you'll be sending data to.
2. `token` The token associated with the specific [Import API integration](https://www.stitchdata.com/docs/integrations/import-api/) within the Stitch Data account.

An example configuration file will look as follows:

```json
{
  "client_id": 1234,
  "token": "foobarfoobar"
}
```

Once the configuration file is created, simply pipe the output of the tap to the Stitch Data target and supply the target with the newly created configuration file:

```bash
$ ~/.venvs/tap-holidays/bin/tap-holidays --config=config/dayforce.config.json --catalog=catalog.json --state=state.json | ~/.venvs/target-stitch/bin/target-stitch --config=config/stitch.config.json >> state.json
$ tail -1 state.json > state.json.tmp
$ mv state.json.tmp state.json
```

## Contributing

The first step to contributing is getting a copy of the source code. First, [fork `tap-holidays` on GitHub](https://github.com/goodeggs/tap-holidays/fork). Then, `cd` into the directory where you want your copy of the source code to live and clone the source code:

```bash
$ git clone git@github.com:YourGitHubName/tap-holidays.git
```

Now that you have a copy of the source code on your local machine, you can leverage [Pipenv](https://docs.pipenv.org/en/latest/) and the corresponding `Pipfile` to install of the development dependencies within a virtual environment:

```bash
$ pipenv install --three --dev
```

This command will create an isolated virtual environment for your `tap-holidays` project and install all the development dependencies defined within the `Pipfile` inside of the environment. You can then enter a shell within the environment:

```bash
$ pipenv shell
```

Or, you can run individual commands within the environment without entering the shell:

```bash
$ pipenv run <command>
```

For example, to format your code using [isort](https://github.com/timothycrosley/isort) and [flake8](http://flake8.pycqa.org/en/latest/index.html) before commiting changes, run the following commands:

```bash
$ pipenv run make isort
$ pipenv run make flake8
```

You can also run the entire testing suite before committing using [tox](https://tox.readthedocs.io/en/latest/):

```bash
$ pipenv run tox
```

Finally, you can run your local version of the tap within the virtual environment using a command like the following:

```bash
$ pipenv run tap-holidays --config=config/dayforce.config.json --catalog=catalog.json
```

Once you've confirmed that your changes work and the testing suite passes, feel free to put out a PR!
