#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_viawarn_us_az_dot import SourceViawarnUsAzDot

if __name__ == "__main__":
    source = SourceViawarnUsAzDot()
    launch(source, sys.argv[1:])
