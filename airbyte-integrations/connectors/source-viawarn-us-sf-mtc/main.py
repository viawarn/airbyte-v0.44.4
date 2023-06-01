#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_viawarn_us_sf_mtc import SourceViawarnUsSfMtc

if __name__ == "__main__":
    source = SourceViawarnUsSfMtc()
    launch(source, sys.argv[1:])
