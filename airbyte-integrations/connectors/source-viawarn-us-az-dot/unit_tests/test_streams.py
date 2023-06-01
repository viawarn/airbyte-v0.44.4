#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import json
from unittest.mock import MagicMock

import pytest
from requests import Response
from source_viawarn_us_az_dot.source import Event, Sign, ViawarnUsAzDotStream

with open("secrets/config.json", "r") as f:
    config = json.load(f)


@pytest.fixture
def patch_base_class(mocker):
    mocker.patch.object(ViawarnUsAzDotStream, "__abstractmethods__", set())


def test_next_page_token(patch_base_class):
    stream = ViawarnUsAzDotStream(config)
    inputs = {"response": MagicMock()}
    expected_token = None
    assert stream.next_page_token(**inputs) == expected_token


def test_request_params(patch_base_class):
    stream = ViawarnUsAzDotStream(config)
    inputs = {"stream_slice": None, "stream_state": None, "next_page_token": None}
    expected_params = {"key":config["developer_api_key"], "format":"json"}
    assert stream.request_params(**inputs) == expected_params


def test_path(patch_base_class):
    stream = Event(config)
    inputs = {"stream_state":None, "stream_slice":None, "next_page_token":None}
    expected_path = "event"
    assert stream.path(**inputs) == expected_path


def test_parse_response_event():
    stream = Event(config)
    # Create an instance of the response object
    response = Response()
    data = [{"ID": "RADS--phoenixazgov-358", "Organization": "RADS", "RoadwayName": "7TH ST - CENTRAL AVE", "DirectionOfTravel": "None", "Description": "7TH ST - CENTRAL AVE - Construction - Roadway improvements LanesRestricted: EB = 1;WB = 1 7TH ST - CENTRAL AVE  Comments: 7th St and Pinnacle Peak - TO- 1500' W/o 7th St", "Reported": 1674457200, "LastUpdated": 1685123452, "StartDate": 1674457200, "PlannedEndDate": 1685516400, "LanesAffected": "No Data", "Latitude": 33.697608, "Longitude": -112.074994, "LatitudeSecondary": 0.0, "LongitudeSecondary": 0.0, "EventType": "roadwork", "IsFullClosure":False, "Restrictions": {"Width": None, "Height": None, "Length": None, "Weight": None, "Speed": None}, "DetourPolyline": "", "DetourInstructions": "", "Recurrence": "", "RecurrenceSchedules": "", "Details": ""}]
    # Convert data to JSON
    json_data = json.dumps(data)
    # add data as the content of response and encode it
    response._content = json_data.encode("utf8")
    expected_parsed_object = {"ID": "RADS--phoenixazgov-358", "Organization": "RADS", "RoadwayName": "7TH ST - CENTRAL AVE", "DirectionOfTravel": "None", "Description": "7TH ST - CENTRAL AVE - Construction - Roadway improvements LanesRestricted: EB = 1;WB = 1 7TH ST - CENTRAL AVE  Comments: 7th St and Pinnacle Peak - TO- 1500' W/o 7th St", "Reported": 1674457200, "LastUpdated": 1685123452, "StartDate": 1674457200, "PlannedEndDate": 1685516400, "LanesAffected": "No Data", "Latitude": 33.697608, "Longitude": -112.074994, "LatitudeSecondary": 0.0, "LongitudeSecondary": 0.0, "EventType": "roadwork", "IsFullClosure": False, "Restrictions": {"Width": None, "Height": None, "Length": None, "Weight": None, "Speed": None}, "DetourPolyline": "", "DetourInstructions": "", "Recurrence": "", "RecurrenceSchedules": "", "Details": "", "vwid": "3e2050aace96fac2b5060559c041fe1c708124b7f43523e1c27ba043f8a5dedd", "ewkt": "SRID=4326;LINESTRING(-112.074994 33.697608,-112.074994 33.697608)"}
    result = stream.parse_response(response,stream_state=MagicMock())
    parsed_object = next(result)
    vwid = parsed_object.get("vwid")
    assert vwid is not None
    expected_parsed_object['vwid'] = vwid
    assert parsed_object == expected_parsed_object


def test_parse_response_sign():
    stream = Sign(config)
    # Create an instance of the response object
    response = Response()
    data = [{"Id": "AZ--4dba5b91-6364-4884-8678-c6c30c9bebeb", "Name": "I-17 SB @ North of SR-69", "Roadway": "I-17", "DirectionOfTravel": "Southbound", "Messages": ["SUNSET POINT\r\nREST AREA CLOSED\r\nSEMI-TRUCKS ONLY", "MINUTES TO\r\nL-303              38\r\nPHOENIX            60"], "Latitude": 34.358546, "Longitude": -112.117519, "LastUpdated": 1685363897}]
    # Convert data to JSON
    json_data = json.dumps(data)
    # add data as the content of response and encode it
    response._content = json_data.encode("utf8")
    expected_parsed_object = {"Id": "AZ--4dba5b91-6364-4884-8678-c6c30c9bebeb", "Name": "I-17 SB @ North of SR-69", "Roadway": "I-17", "DirectionOfTravel": "Southbound", "Messages": ["SUNSET POINT\r\nREST AREA CLOSED\r\nSEMI-TRUCKS ONLY", "MINUTES TO\r\nL-303              38\r\nPHOENIX            60"], "Latitude": 34.358546, "Longitude": -112.117519, "LastUpdated": 1685363897, "vwid": "a061042bc793a792ad9c44c54295f61f4111aa367e64904e2b96bda0b8d4e167", "ewkt": "SRID=4326;POINT(-112.117519 34.358546)"}
    result = stream.parse_response(response,stream_state=MagicMock())
    parsed_object = next(result)
    vwid = parsed_object.get("vwid")
    assert vwid is not None
    expected_parsed_object['vwid'] = vwid
    assert parsed_object == expected_parsed_object
