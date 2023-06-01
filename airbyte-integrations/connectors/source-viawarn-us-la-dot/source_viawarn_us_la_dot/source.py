#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import hashlib
from abc import ABC
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple

import requests
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream

hasher = hashlib.sha256()


# Basic full refresh stream
class ViawarnUsLaDotStream(HttpStream, ABC):

    url_base = "https://511la.org/api/v2/get/"

    def __init__(self, config: Mapping[str, Any], **kwargs):
        super().__init__()
        self.developer_api_key = config["developer_api_key"]

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        return None

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        return {"key": self.developer_api_key, "format": "json"}

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        yield {}


class Event(ViawarnUsLaDotStream):

    primary_key = "vwid"

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "event"

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

        # Extract the response in JSON
        res_dict = response.json()

        # Loop through Edit response to avoid JSON validator issues
        for feature in res_dict:
            id = feature["ID"] + "LA" + "Event"
            hasher.update(id.encode("utf-8"))
            feature["vwid"] = hasher.hexdigest()
            # If there is a secondary lat and lon, then use both coordinates
            # to create a linestring
            # Else, if there is only a primary coordinate, then duplicate the primary coordinates
            # to create a linestring (that is really a point)
            if feature["LongitudeSecondary"] != 0 and feature["LatitudeSecondary"] != 0:
                feature[
                    "ewkt"
                ] = f"SRID=4326;LINESTRING({feature['Longitude']} {feature['Latitude']},{feature['LongitudeSecondary']} {feature['LatitudeSecondary']})"
            else:
                feature[
                    "ewkt"
                ] = f"SRID=4326;LINESTRING({feature['Longitude']} {feature['Latitude']},{feature['Longitude']} {feature['Latitude']})"
            new_dict["features"].append(feature)

        records = new_dict["features"]
        if not records:
            records = []
        yield from records


class Sign(ViawarnUsLaDotStream):

    primary_key = "vwid"

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "messagesigns"

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

        # Extract the response in JSON
        res_dict = response.json()

        # Loop through Edit response to avoid JSON validator issues
        for feature in res_dict:
            id = feature["Id"] + "LA" + "Sign"
            hasher.update(id.encode("utf-8"))
            feature["vwid"] = hasher.hexdigest()
            feature[
                "ewkt"
            ] = f"SRID=4326;LINESTRING({feature['Longitude']} {feature['Latitude']},{feature['Longitude']} {feature['Latitude']})"
            new_dict["features"].append(feature)

        records = new_dict["features"]
        if not records:
            records = []
        yield from records


class Rest(ViawarnUsLaDotStream):

    primary_key = "vwid"

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "restareas"

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

        # Extract the response in JSON
        res_dict = response.json()

        # Loop through Edit response to avoid JSON validator issues
        for feature in res_dict:
            id = feature["Name"] + "LA" + "Rest"
            hasher.update(id.encode("utf-8"))
            feature["vwid"] = hasher.hexdigest()
            feature["ewkt"] = f"SRID=4326;POINT({feature['Longitude']} {feature['Latitude']})"
            new_dict["features"].append(feature)

        records = new_dict["features"]
        if not records:
            records = []
        yield from records


# Source
class SourceViawarnUsLaDot(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, any]:
        try:
            stream = Event(config=config)
            records = stream.read_records(sync_mode=SyncMode.full_refresh)
            next(records)
            return True, None
        except requests.exceptions.RequestException as e:
            return False, e

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        return [Event(config=config), Sign(config=config), Rest(config=config)]