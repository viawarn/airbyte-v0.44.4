#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from unittest.mock import MagicMock

from source_viawarn_us_az_dot.source import SourceViawarnUsAzDot
import json

def test_check_connection(mocker):
    source = SourceViawarnUsAzDot()
    logger_mock = MagicMock()
    with open("secrets/config.json", "r") as f:
        config=json.load(f)
    assert source.check_connection(logger_mock, config) == (True, None)


def test_streams(mocker):
    source = SourceViawarnUsAzDot()
    config_mock = MagicMock()
    streams = source.streams(config_mock)
    # TODO: replace this with your streams number
    expected_streams_number = 2
    assert len(streams) == expected_streams_number
