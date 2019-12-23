import os
from typing import ClassVar, Dict, Iterator, List, Optional, Set

import attr
import backoff
import requests
import singer

from .version import __version__

LOGGER = singer.get_logger()


def is_fatal_code(e: requests.exceptions.RequestException) -> bool:
    '''Helper function to determine if a Requests reponse status code
    is a "fatal" status code. If it is, the backoff decorator will giveup
    instead of attemtping to backoff.'''
    return 400 <= e.response.status_code < 500 and e.response.status_code != 429


@attr.s
class HolidayAPIStream(object):
    tap_stream_id: ClassVar[Optional[str]] = None

    api_key: str = attr.ib()
    config: Dict = attr.ib(repr=False)
    state: Dict = attr.ib()
    api_version: str = attr.ib(default="v1", validator=attr.validators.instance_of(str))
    params: Dict = attr.ib(default=None)
    base_url: str = attr.ib(default="https://holidayapi.com/")

    def __attrs_post_init__(self):
        if self.tap_stream_id is not None:
            self.schema = self._load_schema()

        if self.config.get("streams") is not None:
            self.params = self.config.get("streams", {}).get(self.tap_stream_id, {})
            if not isinstance(self.params, dict):
                raise TypeError("Stream parameters must be supplied as JSON.")
            else:
                for key in self.params.keys():
                    if key not in self.valid_params:
                        raise ValueError(f"{key} is not a valid parameter for stream {self.tap_stream_id}")

                for param in self.required_params:
                    if param not in self.params.keys():
                        raise ValueError(f"{param} is a required parameter for stream {self.tap_stream_id}")

    @classmethod
    def from_args(cls, args):
        return cls(api_key=args.config.get("api_key"),
                   api_version=args.config.get("api_version"),
                   config=args.config,
                   state=args.state)

    def _get_abs_path(self, path: str) -> str:
        return os.path.join(os.path.dirname(os.path.realpath(__file__)), path)

    def _load_schema(self) -> Dict:
        '''Loads a JSON schema file for a given
        Dayforce resource into a dict representation.
        '''
        schema_path = self._get_abs_path("schemas")
        return singer.utils.load_json(f"{schema_path}/{self.tap_stream_id}.json")

    def _construct_headers(self) -> Dict:
        '''Constructs a standard set of headers for HTTPS requests.'''
        headers = requests.utils.default_headers()
        headers["User-Agent"] = f"python-holidays-tap/{__version__}"
        headers["Date"] = singer.utils.strftime(singer.utils.now(), '%a, %d %b %Y %H:%M:%S %Z')
        return headers

    @backoff.on_exception(backoff.fibo,
                          requests.exceptions.HTTPError,
                          max_time=120,
                          giveup=is_fatal_code,
                          logger=LOGGER)
    @backoff.on_exception(backoff.fibo,
                          (requests.exceptions.ConnectionError,
                           requests.exceptions.Timeout),
                          max_time=120,
                          logger=LOGGER)
    def _get(self, endpoint: str, params: Dict = None) -> Dict:
        '''Constructs a standard way of making
        a GET request to the Holiday API.
        '''
        url = self.base_url + self.api_version + endpoint
        headers = self._construct_headers()
        self.params.update({"key": self.api_key})
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        return response.json()

    def _yield_records(self, entity: str, params: Dict = None) -> Iterator[Dict]:
        '''Yeild individual records for a given entity.'''
        records = self._get(endpoint=f"/{entity}", params=params).get(entity)
        for record in records:
            yield record

    def sync(self):
        '''Sync data according to Singer spec.'''
        with singer.metrics.job_timer(job_type=f"sync_{self.tap_stream_id}"):
            with singer.metrics.record_counter(endpoint=self.tap_stream_id) as counter:
                for record in self._yield_records(entity=self.tap_stream_id, params=self.params):
                    with singer.Transformer() as transformer:
                        transformed_record = transformer.transform(data=record, schema=self.schema)
                        singer.write_record(stream_name=self.tap_stream_id, time_extracted=singer.utils.now(), record=transformed_record)
                        counter.increment()

    def write_schema_message(self):
        '''Writes a Singer schema message.'''
        return singer.write_schema(stream_name=self.tap_stream_id, schema=self.schema, key_properties=self.key_properties)

    def write_state_message(self):
        '''Writes a Singer state message.'''
        return singer.write_state(self.state)


@attr.s
class HolidayStream(HolidayAPIStream):
    tap_stream_id: ClassVar[str] = 'holidays'
    key_properties: ClassVar[List[str]] = ["uuid", "date"]
    bookmark_properties: ClassVar[List[str]] = []
    replication_method: ClassVar[str] = 'full_table'
    required_params: ClassVar[Set[str]] = {
        "country",
        "year"
    }
    valid_params: ClassVar[Set[str]] = {
        "country",
        "year",
        "month",
        "day",
        "previous",
        "upcoming",
        "public",
        "subdivisions",
        "search",
        "language"
    }
