#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (C) 2025 Your Company
# License: GNU General Public License v2

"""
Server Side Call for Extreme Cloud IQ Special Agent

This file defines the rule configuration interface for the special agent.

Install to: local/lib/python3/cmk_addons/plugins/xiq_agent/server_side_calls/special_agent.py
"""


#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from collections.abc import Iterator
from typing import Any
from pydantic import BaseModel

from cmk.server_side_calls.v1 import (
    HostConfig,
    SpecialAgentCommand,
    SpecialAgentConfig,
)

class TokenAuth(BaseModel):
    token: Any

class AuthCredentials(BaseModel):
    username: str
    password: Any

class Params(BaseModel):
    authentication: tuple[str, AuthCredentials | TokenAuth | Any]
    timeout: int | None = None
    no_cert_check: tuple[str, dict] | None = None

def generate_extreme_cloud_iq_command(
    params: Params,
    host_config: HostConfig, # Das Argument muss bleiben (API-Vorgabe)
) -> Iterator[SpecialAgentCommand]:
    
    args: list[Any] = []
    
    auth_method, auth_value = params.authentication
    
    if auth_method == "token":
        if isinstance(auth_value, TokenAuth):
            args += ["--api-token", auth_value.token]
        elif isinstance(auth_value, dict):
            args += ["--api-token", auth_value.get("token")]
    elif auth_method == "credentials":
        if isinstance(auth_value, AuthCredentials):
            args += ["--username", auth_value.username]
            args += ["--password", auth_value.password]

    if params.timeout is not None:
        args += ["--timeout", str(params.timeout)]
    
    if params.no_cert_check is not None:
        check_method, _ = params.no_cert_check
        if check_method == "no_verify":
            args.append("--no-cert-check")
    

    
    yield SpecialAgentCommand(command_arguments=args)

special_agent_extreme_cloud_iq = SpecialAgentConfig(
    name="extreme_cloud_iq",
    parameter_parser=Params.model_validate,
    commands_function=generate_extreme_cloud_iq_command,
)