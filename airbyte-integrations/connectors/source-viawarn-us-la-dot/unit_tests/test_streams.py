#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import json
from unittest.mock import MagicMock

import pytest
from requests import Response
from source_viawarn_us_la_dot.source import Event, ViawarnUsLaDotStream

with open("secrets/config.json","r") as f:
    config = json.load(f)


@pytest.fixture
def patch_base_class(mocker):
    mocker.patch.object(ViawarnUsLaDotStream, "__abstractmethods__", set())


def test_request_params(patch_base_class):
    stream = ViawarnUsLaDotStream(config)
    inputs = {"stream_slice": None, "stream_state": None, "next_page_token": None}
    expected_params = {"key":config['developer_api_key'], "format":"json"}
    assert stream.request_params(**inputs) == expected_params


def test_next_page_token(patch_base_class):
    stream = ViawarnUsLaDotStream(config)
    inputs = {"response": MagicMock()}
    expected_token = None
    assert stream.next_page_token(**inputs) == expected_token


def test_path(patch_base_class):
    stream = Event(config)
    inputs = {"stream_state":None, "stream_slice":None, "next_page_token":None}
    expected_path = "event"
    assert stream.path(**inputs) == expected_path


def test_parse_response_event():
    stream = Event(config)
    response = Response()
    data = [{"ID": "ERS--34696", "Organization": "ERS", "RoadwayName": "US-90", "DirectionOfTravel": "Both Directions", "Description": "Road Construction on US-90 Both Directions from Harding St   to Dakin St  . Lanes Alternating.  Starting 1/9/2022 9:00 PM ", "Reported": 1641783600, "LastUpdated": 1641576513, "StartDate": 1641783600, "PlannedEndDate": None, "LanesAffected": "Lanes Alternating", "Latitude": 29.9623, "Longitude": -90.142201, "LatitudeSecondary": 29.964431, "LongitudeSecondary": -90.131995, "EventType": "roadwork", "IsFullClosure": False, "Restrictions": {"Width": None, "Height": None, "Length": None, "Weight": None, "Speed": None}, "DetourPolyline": None, "DetourInstructions": None, "Recurrence": "<b>Sun, Mon, Tue, Wed, Thu, Fri, Sat:</b><br/>Active all day<br/><br/>", "RecurrenceSchedules": [{"StartDate": "1/9/2022 9:00:00 PM-05:00:00", "EndDate": None, "Times": [{"StartTime": "00:00:00-05:00:00", "EndTime": "23:59:59-05:00:00"}], "DaysOfWeek": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]}], "EventSubType": "roadconstruction", "Details": "Eastbound and Westbound Jefferson Highway (US 90), from Harding Street to Dakin Street, in Elmwood/Jefferson - alternating single continuous lane closure starting Sunday, January 9, 2022 at 9:00 PM until further notice; while crews perform asphalt and concrete work. "}]
    # Convert data to JSON
    json_data = json.dumps(data)
    # add data as the content of response and encode it
    response._content = json_data.encode("utf8")
    expected_parsed_object = {"ID": "ERS--34696", "Organization": "ERS", "RoadwayName": "US-90", "DirectionOfTravel": "Both Directions", "Description": "Road Construction on US-90 Both Directions from Harding St   to Dakin St  . Lanes Alternating.  Starting 1/9/2022 9:00 PM ", "Reported": 1641783600, "LastUpdated": 1641576513, "StartDate": 1641783600, "PlannedEndDate": None, "LanesAffected": "Lanes Alternating", "Latitude": 29.9623, "Longitude": -90.142201, "LatitudeSecondary": 29.964431, "LongitudeSecondary": -90.131995, "EventType": "roadwork", "IsFullClosure": False, "Restrictions": {"Width": None, "Height": None, "Length": None, "Weight": None, "Speed": None}, "DetourPolyline": None, "DetourInstructions": None, "Recurrence": "<b>Sun, Mon, Tue, Wed, Thu, Fri, Sat:</b><br/>Active all day<br/><br/>", "RecurrenceSchedules": [{"StartDate": "1/9/2022 9:00:00 PM-05:00:00", "EndDate": None, "Times": [{"StartTime": "00:00:00-05:00:00", "EndTime": "23:59:59-05:00:00"}], "DaysOfWeek": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]}], "EventSubType": "roadconstruction", "Details": "Eastbound and Westbound Jefferson Highway (US 90), from Harding Street to Dakin Street, in Elmwood/Jefferson - alternating single continuous lane closure starting Sunday, January 9, 2022 at 9:00 PM until further notice; while crews perform asphalt and concrete work. ", "vwid": "71b31b4c6d81f3192be66840f51c858b6a033cbb7c7568aa4957f1d48c30c5fb", "ewkt": "SRID=4326;LINESTRING(-90.142201 29.9623,-90.131995 29.964431)"}
    result = stream.parse_response(response,stream_state=MagicMock())
    parsed_object = next(result)
    vwid = parsed_object.get("vwid")
    assert vwid is not None
    expected_parsed_object['vwid'] = vwid
    assert parsed_object == expected_parsed_object
