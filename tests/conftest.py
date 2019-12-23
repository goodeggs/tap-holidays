import argparse
import json

import pytest

from tap_holidays.client import HolidayStream


@pytest.fixture(scope='function')
def config(shared_datadir):
    with open(shared_datadir / 'test.config.json') as f:
        return json.load(f)


@pytest.fixture(scope='function')
def args(config, shared_datadir):
    args = argparse.Namespace()
    setattr(args, 'config', config)
    setattr(args, 'state', {})
    setattr(args, 'config_path', shared_datadir / 'test.config.json')
    return args


@pytest.fixture(scope='function', params={HolidayStream})
def client(config, args, shared_datadir, request):
    return request.param(api_key=config.get("api_key"),
                         api_version=config.get("api_version"),
                         config=config,
                         state=args.state)
