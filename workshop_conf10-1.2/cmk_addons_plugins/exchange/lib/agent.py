#!/usr/bin/env python3
# Copyright (C) 2019 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.

__version__ = "2.4.0b1"

import argparse
import json
import sys

import requests


# NEW: parse number of packages for summary section
def parse_arguments(argv):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--packagecount", type=int, default=5, help="Number of top downloaded packages to return"
    )
    return parser.parse_args(argv)


def main(sys_argv=None):
    args = parse_arguments(sys_argv or sys.argv[1:])
    num_top_packages = args.packagecount

    top_download_url = "https://exchange.checkmk.com/api/packages/downloads/20"
    top_downloaded_packages = requests.get(top_download_url).json()["packages"]

    sys.stdout.write("<<<exchange_packages_summary:sep(0)>>>\n")
    for pkg in top_downloaded_packages[:num_top_packages]:
        sys.stdout.write(f"{json.dumps(pkg)}\n")

    robotmk_id = 375
    yum_update_id = 362
    explicit_package_ids = [robotmk_id, yum_update_id]

    sys.stdout.write("<<<exchange_packages:sep(0)>>>\n")
    for pkg in top_downloaded_packages:
        if pkg["id"] in explicit_package_ids:
            sys.stdout.write(f"{json.dumps(pkg)}\n")


if __name__ == "__main__":
    main()
