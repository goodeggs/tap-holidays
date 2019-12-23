import pytest
import requests
import responses
from singer.schema import Schema

from tap_holidays.client import HolidayStream, is_fatal_code


@pytest.mark.parametrize('status_code', [400, 401, 403, 404,
                                         pytest.param(500, marks=pytest.mark.xfail),
                                         pytest.param(502, marks=pytest.mark.xfail),
                                         pytest.param(503, marks=pytest.mark.xfail),
                                         pytest.param(504, marks=pytest.mark.xfail)])
def test_is_fatal_code(status_code):
    resp = requests.models.Response()
    resp.status_code = status_code
    exc = requests.exceptions.RequestException(response=resp)
    assert is_fatal_code(exc)


@pytest.mark.parametrize('pt_stream', [HolidayStream])
def test_client_from_args_class_method(pt_stream, args, config, shared_datadir):
    stream = pt_stream.from_args(args)
    assert stream.api_key == "foobar123"
    assert stream.api_version == "v1"
    assert stream.config == config
    assert stream.state == args.state


def test_load_schema(client):
    schema = client._load_schema()
    assert isinstance(schema, dict)
    assert Schema.from_dict(schema)


def test_get_successful(client):
    with responses.RequestsMock() as rsps:
        expected = {client.tap_stream_id: [{"name": "SuperBowl"}, {"name": "Thanksgiving"}]}
        rsps.add(responses.GET, f"{client.base_url}{client.api_version}/{client.tap_stream_id}",
                 json=expected, status=200)
        resp = client._get(endpoint=f"/{client.tap_stream_id}")
        assert resp == expected


@pytest.mark.xfail()
@pytest.mark.parametrize('status_code', [400, 401, 403, 404])
def test_get_fatal(client, status_code):
    with responses.RequestsMock() as rsps:
        expected = {}
        rsps.add(responses.GET, f"{client.base_url}{client.api_version}/{client.tap_stream_id}",
                 json=expected, status=status_code)
        resp = client._get(endpoint=f"/{client.tap_stream_id}")
        assert resp == expected
