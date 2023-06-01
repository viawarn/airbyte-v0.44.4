#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from unittest.mock import MagicMock

from source_viawarn_us_ak_dot.source import SourceViawarnUsAkDot

import json

def test_check_connection(mocker):
    source = SourceViawarnUsAkDot()
    with open("secrets/config.json", "r") as f:
        config = json.load(f)
    logger_mock = MagicMock()
    assert source.check_connection(logger_mock,config) == (True, None)


def test_streams(mocker):
    source = SourceViawarnUsAkDot()
    config_mock = MagicMock()
    streams = source.streams(config_mock)
    # TODO: replace this with your streams number
    expected_streams_number = 3
    assert len(streams) == expected_streams_number

