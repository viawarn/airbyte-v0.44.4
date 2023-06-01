#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_viawarn_us_ak_dot import SourceViawarnUsAkDot

if __name__ == "__main__":
    source = SourceViawarnUsAkDot()
    launch(source, sys.argv[1:])
