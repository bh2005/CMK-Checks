#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (C) 2026 bh2005
# License: GNU General Public License v2

"""
Agent Configuration for Extreme Cloud IQ Special Agent
Checkmk 2.4 Edition
"""

from collections.abc import Iterator
from typing import Any  # Wichtig für die Passwort-Metadaten
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
    password: Any  # Nutze Any, um ValueError durch Checkmk-Metadaten zu vermeiden


class Params(BaseModel):
    """Parameters for the Extreme Cloud IQ special agent"""
    # Das Mapping passt nun exakt zu CascadingSingleChoice
    authentication: tuple[str, AuthCredentials | Any] 
    timeout: int | None = None
    no_cert_check: tuple[str, dict] | None = None


def generate_extreme_cloud_iq_command(
    params: Params,
    host_config: HostConfig,
) -> Iterator[SpecialAgentCommand]:
    """Generate the command line for the special agent"""
    
    # Checkmk 2.4 nutzt primary_address für die Host-IP
    args: list[Any] = [host_config.primary_address]
    
    # Authentication Logik
    auth_method, auth_value = params.authentication
    
    if auth_method == "credentials":
        if isinstance(auth_value, AuthCredentials):
            args += ["--username", auth_value.username]
            # Kein .unsafe() mehr! Das macht Checkmk jetzt sicher im Hintergrund
            args += ["--password", auth_value.password]
    elif auth_method == "token":
        # auth_value ist hier das verschlüsselte Token-Tupel
        args += ["--api-token", auth_value]
    
    # Optional timeout
    if params.timeout is not None:
        args += ["--timeout", str(params.timeout)]
    
    # SSL certificate check (CascadingSingleChoice)
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