#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import hashlib
import json
from abc import ABC
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple

import requests
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream

hasher = hashlib.sha256()


class ViawarnUsSfMtcStream(HttpStream, ABC):

    url_base = "http://api.511.org/"

    def __init__(self, config: Mapping[str, Any], **kwargs):
        super().__init__()
        self.developer_api_key = config["developer_api_key"]
        self.request_limit = config["request_limit"]

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        decoded_response = json.loads(response.content.decode("'utf-8-sig'"))
        # Walrus operator := declare pagination variable and returns its value for evaluation
        if (pagination := decoded_response.get("pagination")) and pagination.get("next_url"):
            return {"offset": pagination.get("offset") + self.request_limit}

        else:
            return None

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        params = {"api_key": self.developer_api_key}
        params["limit"] = self.request_limit
        if next_page_token:
            params.update(next_page_token)
        return params

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        yield {}

    def backoff_time(self, response: requests.Response) -> Optional[float]:
        """* Response does not provide any time for a next tried in the request headers (while the request does not excede the request-rate limit)
        * Docs do not provide information about request headers while exceding the request-rate limit (60 requests per 3600s)
        Then, assignig 600s, considering that errors could be induced not just by reaching request-rate limit but for reaching the time_out or any another failure
        """
        self.logger.info("Retry-after header not found. Using default backoff value")
        return 600


class Event(ViawarnUsSfMtcStream):

    primary_key = "vwid"

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "traffic/events"

    def parse_response(
        self,
        response: requests.Response,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> Iterable[Mapping]:
        # Create a dictionary to store the features from the source.
        new_dict = {}
        new_dict["features"] = []

        # defining encoding
        response.encoding = "'utf-8-sig'"
        # with open("jsonprobe_limit.json", "w") as f:
        #     f.write(response.content.decode("'utf-8-sig'"))
        res_dict = response.json()

        # Loop through Edit response to avoid JSON validator issues
        for feature in res_dict["events"]:
            # feature['vwid'] = str(uuid.uuid4())
            id = str(feature["id"]) + "SF" + "Event"
            hasher.update(id.encode("utf-8"))
            feature["vwid"] = hasher.hexdigest()
            coords = ""

            if feature["geography"]["type"] == "Point":
                coords = f"{feature['geography']['coordinates'][0]} {feature['geography']['coordinates'][1]}, {feature['geography']['coordinates'][0]} {feature['geography']['coordinates'][1]}"
            if feature["geography"]["type"] == "LineString":
                for point in feature["geography"]["coordinates"]:
                    coords = coords + f"{point[0]} {point[1]},"
                coords = coords[:-1]
            feature["ewkt"] = f"SRID=4326;LINESTRING({coords})"
            # MultiLineString.
            # if feature['geography']['type'] == 'MultiLineString':
            # for linestring in feature['geography']['coordinates']:
            #     coords = ""
            #     for point in linestring:
            #         coords = coords + f"{point[0]} {point[1]},"
            #     coords = coords[:-1]
            #     multiline_coords.append(f"({coords})")
            # ewkt = "MULTILINESTRING(" + ",".join(multiline_coords) + ")"
            # feature['ewkt'] = f"SRID=4326;{ewkt}"

            # MultiPoint,
            # if feature['geography']['type'] == 'MultiPoint':

            # for point in feature['geography']['coordinates']:
            #     coords = coords + f"{point[0]} {point[1]},"
            # coords = coords[:-1]
            # feature['ewkt'] = f"SRID=4326;MULTIPOINT({coords})"

            # Polygon
            # if feature['geography']['type'] == 'Polygon':
            # for ring in feature['geography']['coordinates']:
            #     ring_coords = ""
            #     for point in ring:
            #         ring_coords = ring_coords + f"{point[0]} {point[1]},"
            #     ring_coords = ring_coords[:-1]
            #     coords = coords + f"({ring_coords}),"
            # coords = coords[:-1]
            # feature['ewkt'] = f"SRID=4326;POLYGON(({coords}))"

            new_dict["features"].append(feature)

        records = new_dict["features"]
        if not records:
            records = []
        yield from records


# Source
class SourceViawarnUsSfMtc(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, any]:
        try:
            stream = Event(config=config)
            records = stream.read_records(sync_mode=SyncMode.full_refresh)
            next(records)
            return True, None
        except requests.exceptions.RequestException as e:
            return False, e

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        return [Event(config=config)]
