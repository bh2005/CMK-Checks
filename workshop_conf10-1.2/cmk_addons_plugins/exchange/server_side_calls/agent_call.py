#!/usr/bin/env python3
# Copyright (C) 2024 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.

from collections.abc import Iterator, Mapping
from typing import Any

from cmk.server_side_calls.v1 import (
    HostConfig,
    noop_parser,
    SpecialAgentCommand,
    SpecialAgentConfig,
)


def generate_command(
    params: Mapping[str, Any],
    host_config: HostConfig,
) -> Iterator[SpecialAgentCommand]:
    # NEW: pass number of packages (configured in ruleset) to agent
    args = ["--packagecount", str(params["package_count"])]
    yield SpecialAgentCommand(command_arguments=args)


special_agent_exchange = SpecialAgentConfig(
    name="exchange",
    parameter_parser=noop_parser,
    commands_function=generate_command,
)
