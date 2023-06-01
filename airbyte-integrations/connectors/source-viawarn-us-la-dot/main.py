#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_viawarn_us_la_dot import SourceViawarnUsLaDot

if __name__ == "__main__":
    source = SourceViawarnUsLaDot()
    launch(source, sys.argv[1:])
