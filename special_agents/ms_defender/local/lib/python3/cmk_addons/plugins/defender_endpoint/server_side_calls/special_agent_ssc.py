#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Call-Konfiguration: Verknüpft GUI-Einstellungen mit den CLI-Argumenten des Special Agents.
Ablage: ~/local/lib/python3/cmk_addons/plugins/defender_endpoint/server_side_calls/special_agent.py
"""

from collections.abc import Iterator
from cmk.server_side_calls.v1 import (
    SpecialAgentConfig,
    SpecialAgentCommand,
)
from pydantic import BaseModel


class DefenderEndpointParams(BaseModel):
    """Validierungsmodell für die GUI-Parameter."""
    tenant_id:     str
    client_id:     str
    client_secret: str | tuple  # tuple wenn aus dem Passwort-Store


def _agent_arguments(params: DefenderEndpointParams, host_config) -> Iterator[SpecialAgentCommand]:
    """Baut die CLI-Argumente für den Special Agent zusammen."""

    # client_secret kann ein Plain-String oder ein Passwort-Store-Tuple sein
    if isinstance(params.client_secret, tuple):
        # Passwort-Store: ("password", "der-geheime-wert")
        secret_value = params.client_secret[1]
    else:
        secret_value = params.client_secret

    yield SpecialAgentCommand(
        command_arguments=[
            "--tenant-id",     params.tenant_id,
            "--client-id",     params.client_id,
            "--client-secret", secret_value,
        ]
    )


def _parameter_parser(raw_params: dict) -> DefenderEndpointParams:
    return DefenderEndpointParams(**raw_params)


special_agent_defender_endpoint = SpecialAgentConfig(
    name="defender_endpoint",
    parameter_parser=_parameter_parser,
    commands_function=_agent_arguments,
)