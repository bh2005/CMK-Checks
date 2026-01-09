#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (C) 2025 bh2005
# License: GNU General Public License v2

"""
Agent Configuration for Extreme Cloud IQ Special Agent

This file defines how the special agent is called with its parameters.

Install to: local/lib/python3/cmk_addons/plugins/xiq_agent/server_side_calls/special_agent.py
"""

from collections.abc import Iterator
from pydantic import BaseModel

from cmk.server_side_calls.v1 import (
    HostConfig,
    Secret,
    SpecialAgentCommand,
    SpecialAgentConfig,
)


class AuthCredentials(BaseModel):
    """Username and password authentication"""
    username: str
    password: Secret


class Params(BaseModel):
    """Parameters for the Extreme Cloud IQ special agent"""
    authentication: tuple[str, AuthCredentials | Secret]
    timeout: int | None = None
    no_cert_check: tuple[str, None] | None = None


def generate_extreme_cloud_iq_command(
    params: Params,
    host_config: HostConfig,
) -> Iterator[SpecialAgentCommand]:
    """Generate the command line for the special agent"""
    
    args: list[str | Secret] = []
    
    # Authentication
    auth_method, auth_value = params.authentication
    
    if auth_method == "credentials":
        if isinstance(auth_value, AuthCredentials):
            args += ["--username", auth_value.username]
            args += ["--password", auth_value.password.unsafe()]
    elif auth_method == "token":
        if isinstance(auth_value, Secret):
            args += ["--api-token", auth_value.unsafe()]
    
    # Optional timeout
    if params.timeout is not None:
        args += ["--timeout", str(params.timeout)]
    
    # SSL certificate check
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
