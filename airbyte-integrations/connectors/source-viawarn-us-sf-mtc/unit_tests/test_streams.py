#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import json
from unittest.mock import MagicMock

import pytest
from requests import Response
from source_viawarn_us_sf_mtc.source import Event, ViawarnUsSfMtcStream

with open("secrets/config.json", "r") as f:
    config = json.load(f)


@pytest.fixture
def patch_base_class(mocker):
    mocker.patch.object(ViawarnUsSfMtcStream, "__abstractmethods__", set())


def test_request_params(patch_base_class):
    stream = ViawarnUsSfMtcStream(config)
    inputs = {"stream_slice": None, "stream_state": None, "next_page_token": None}
    expected_params = {"api_key":config["developer_api_key"], "limit":100}
    assert stream.request_params(**inputs) == expected_params


def test_next_page_token(patch_base_class):
    stream = ViawarnUsSfMtcStream(config)
    data = {
        "events":[{
                "url": "/traffic/events/511.org/1045578",
                "jurisdiction_url": "http://api.511.org/jurisdictions/",
                "id": "511.org/1045578",
                "status": "ACTIVE",
                "headline": "CHP : Disabled vehicle on I-80 Eastbound west of I-505 N (Vacaville). Lane affected. Expect delays.",
                "event_type": "INCIDENT",
                "event_subtypes": [
                    "Disabled vehicle"
                ],
                "severity": "Moderate",
                "created": "2023-05-31T13:17Z",
                "updated": "2023-05-31T13:17Z",
                "areas": [
                    {
                        "name": "Solano",
                        "id": 5396987,
                        "url": "http://geonames.org/5396987/"
                    }
                ],
                "geography": {
                    "type": "Point",
                    "crs": {
                        "type": "name",
                        "properties": {
                            "name": "urn:ogc:def:crs:EPSG::4326"
                        }
                    },
                    "coordinates": [
                        -121.950177,
                        38.375466
                    ]
                },
                "+source_type": "CHP",
                "+source_id": "230531GG00285",
                "roads": [
                    {
                        "name": "I-80 E",
                        "from": "I-505 N",
                        "direction": "Eastbound",
                        "state": "SOME_LANES_CLOSED",
                        "+lane_type": "Lane",
                        "+lane_status": "affected",
                        "+road_advisory": "Expect delays",
                        "+article": "west of"
                    }
                ],
                "schedule": {
                    "intervals": ["2023-05-31T13:17Z/"]
                }
            }
        ],
        "pagination": {
            "offset": 0,
            "next_url": "/traffic/events?api_key=ff945e3c-7502-4d7d-89b8-ca7365dc097f&request_limit=10&limit=20&offset=20"
        },
        "meta": {
            "url": "/traffic/events?api_key=ff945e3c-7502-4d7d-89b8-ca7365dc097f&request_limit=10",
            "up_url": "/",
            "version": "v1"
        }
    }
    # Convert data to JSON
    json_data = json.dumps(data)
    # add data as the content of response and encode it
    response = Response()
    response._content = json_data.encode("utf8")
    # TODO: replace this with your expected next page token
    expected_token = {"offset": 100}
    assert stream.next_page_token(response) == expected_token


def test_backoff_time(patch_base_class):
    response_mock = MagicMock()
    stream = ViawarnUsSfMtcStream(config)
    expected_backoff_time = 600
    assert stream.backoff_time(response_mock) == expected_backoff_time


def test_path(patch_base_class):
    stream = Event(config)
    inputs = {"stream_state":None, "stream_slice":None, "next_page_token":None}
    expected_path = "traffic/events"
    assert stream.path(**inputs) == expected_path


def test_parse_response_event():
    stream = Event(config)
    # Create an instance of the response object
    response = Response()
    data = {"events":[{"url": "/traffic/events/511.org/1045617", "jurisdiction_url": "http://api.511.org/jurisdictions/", "id": "511.org/1045617", "status": "ACTIVE", "headline": "CHP : Traffic Collision on US-101 Northbound at Tennant Ave (Morgan Hill). Lane affected. Expect delays.", "event_type": "INCIDENT", "event_subtypes": ["Traffic Collision"], "severity": "Moderate", "created": "2023-05-31T15:46Z", "updated": "2023-05-31T16:17Z", "areas": [{"name": "Santa Clara", "id": 5393021, "url": "http://geonames.org/5393021/"}], "geography": {"type": "Point", "crs": {"type": "name", "properties": {"name": "urn:ogc:def:crs:EPSG::4326"}}, "coordinates": [-121.625833, 37.119167]}, "+source_type": "CHP", "+source_id": "230531MY00084", "roads": [{"name": "US-101 N", "from": "Tennant Ave", "direction": "Northbound", "state": "SOME_LANES_CLOSED", "+lane_type": "Lane", "+lane_status": "affected", "+road_advisory": "Expect delays", "+article": "at"}], "schedule": {"intervals": ["2023-05-31T16:17Z/"]}, "vwid": "c26dd86bbd4e8a72f396a05293a1c3ea0c093c42875d437afb074e24ee3670a4", "ewkt": "SRID=4326;LINESTRING(-121.625833 37.119167, -121.625833 37.119167)"}],
            "pagination": {"offset": 0, "next_url": "/traffic/events?api_key=ff945e3c-7502-4d7d-89b8-ca7365dc097f&request_limit=10&limit=20&offset=20"},
            "meta": {"url": "/traffic/events?api_key=ff945e3c-7502-4d7d-89b8-ca7365dc097f&request_limit=10","up_url": "/", "version": "v1"}
            }
    # Convert data to JSON
    json_data = json.dumps(data)
    # add data as the content of response and encode it
    response = Response()
    response._content = json_data.encode("utf8")
    expected_parsed_object = {"url": "/traffic/events/511.org/1045617", "jurisdiction_url": "http://api.511.org/jurisdictions/", "id": "511.org/1045617", "status": "ACTIVE", "headline": "CHP : Traffic Collision on US-101 Northbound at Tennant Ave (Morgan Hill). Lane affected. Expect delays.", "event_type": "INCIDENT", "event_subtypes": ["Traffic Collision"], "severity": "Moderate", "created": "2023-05-31T15:46Z", "updated": "2023-05-31T16:17Z", "areas": [{"name": "Santa Clara", "id": 5393021, "url": "http://geonames.org/5393021/"}], "geography": {"type": "Point", "crs": {"type": "name", "properties": {"name": "urn:ogc:def:crs:EPSG::4326"}}, "coordinates": [-121.625833, 37.119167]}, "+source_type": "CHP", "+source_id": "230531MY00084", "roads": [{"name": "US-101 N", "from": "Tennant Ave", "direction": "Northbound", "state": "SOME_LANES_CLOSED", "+lane_type": "Lane", "+lane_status": "affected", "+road_advisory": "Expect delays", "+article": "at"}], "schedule": {"intervals": ["2023-05-31T16:17Z/"]}, "vwid": "c26dd86bbd4e8a72f396a05293a1c3ea0c093c42875d437afb074e24ee3670a4", "ewkt": "SRID=4326;LINESTRING(-121.625833 37.119167, -121.625833 37.119167)"}
    result = stream.parse_response(response,stream_state=MagicMock())
    parsed_object = next(result)
    vwid = parsed_object.get("vwid")
    assert vwid is not None
    expected_parsed_object['vwid'] = vwid
    assert parsed_object == expected_parsed_object
