#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import json
from unittest.mock import MagicMock

from source_viawarn_us_la_dot.source import SourceViawarnUsLaDot


def test_check_connection(mocker):
    source = SourceViawarnUsLaDot()
    logger_mock = MagicMock()
    with open("secrets/config.json", "r") as f:
        config = json.load(f)
    assert source.check_connection(logger_mock, config) == (True, None)


def test_streams(mocker):
    source = SourceViawarnUsLaDot()
    config_mock = MagicMock()
    streams = source.streams(config_mock)
    # TODO: replace this with your streams number
    expected_streams_number = 3
    assert len(streams) == expected_streams_number
