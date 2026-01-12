#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from collections.abc import Iterator
from typing import Any # Wichtig für die Passwort-Metadaten
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
    password: Any # Erlaubt die Übergabe der verschlüsselten Checkmk-Daten

class Params(BaseModel):
    """Parameters for the Extreme Cloud IQ special agent"""
    # Das Tuple-Format entspricht der Rückgabe von CascadingSingleChoice
    authentication: tuple[str, AuthCredentials | Any]
    timeout: int | None = None
    no_cert_check: tuple[str, dict] | None = None

def generate_extreme_cloud_iq_command(
    params: Params,
    host_config: HostConfig,
) -> Iterator[SpecialAgentCommand]:
    """Generate the command line for the special agent"""
    
    # In Checkmk 2.4 nutzen wir primary_address für die Host-IP
    args: list[Any] = [host_config.primary_address]
    
    auth_method, auth_value = params.authentication
    
    if auth_method == "credentials":
        if isinstance(auth_value, AuthCredentials):
            args += ["--username", auth_value.username]
            # Kein .unsafe() mehr nötig! 
            args += ["--password", auth_value.password]
    elif auth_method == "token":
        # auth_value ist hier direkt das verschlüsselte Token-Objekt
        args += ["--api-token", auth_value]
    
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