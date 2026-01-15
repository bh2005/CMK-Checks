# -*- coding: utf-8 -*-
# Dateipfad: ~/local/lib/python3/cmk_addons/plugins/xiq_agent/server_side_calls/special_agent.py

from typing import Any, Mapping

from cmk.server_side_calls.v1 import (
    SpecialAgentCommand,
    SpecialAgentConfig,
    HostConfig,
    noop_parser,
)

def _agent_arguments(
    params: Mapping[str, Any],
    host_config: HostConfig,
) -> list[SpecialAgentCommand]:
    args: list[str] = []

    # URL mit Default
    url = params.get("url", "https://api.extremecloudiq.com")
    args.extend(["--url", url])

    # Username & Password (Pflicht)
    username = params.get("username")
    password = params.get("password")

    if not username or not password:
        raise ValueError("Username und Password sind Pflichtfelder")

    args.extend(["--username", username])
    args.extend(["--password", password.unsafe()])

    # Hostname für Cache
    args.extend(["--host", host_config.name])

    # Insecure Flag
    if params.get("no_cert_check", "no") == "yes":
        args.append("--no-cert-check")

    yield SpecialAgentCommand(command_arguments=args)

special_agent_extreme_cloud_iq = SpecialAgentConfig(
    name="xiq_agent",
    parameter_parser=noop_parser,
    commands_function=_agent_arguments,
)