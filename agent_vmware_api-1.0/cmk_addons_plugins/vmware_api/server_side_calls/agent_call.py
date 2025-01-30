#!/usr/bin/env python3
# -*- encoding: utf-8; py-indent-offset: 4 -*-

# (c) Stefan Mühling <muehling.stefan@googlemail.com>

# License: GNU General Public License v2

from collections.abc import Iterator
from pydantic import BaseModel

from cmk.server_side_calls.v1 import (
    HostConfig,
    Secret,
    SpecialAgentCommand,
    SpecialAgentConfig,
)


class Params(BaseModel):
    """params validator"""
    username: str | None = None
    password: Secret | None = None
    port: int | None = None
    verify_ssl: bool | None = True

def _agent_vmware_api_arguments(
    params: Params, host_config: HostConfig
) -> Iterator[SpecialAgentCommand]:
    command_arguments: list[str | Secret] = []
    if params.username is not None:
        command_arguments += ["--username", params.username]
    if params.password is not None:
        command_arguments += ["--password-id", params.password]
    if params.port is not None:
        command_arguments += ["-p", str(params.port)]
    if params.verify_ssl is True:
        command_arguments += ["--verify-ssl"]
    command_arguments.append(host_config.primary_ip_config.address or host_config.name)
    yield SpecialAgentCommand(command_arguments=command_arguments)

special_agent_vmware_api = SpecialAgentConfig(
    name="vmware_api",
    parameter_parser=Params.model_validate,
    commands_function=_agent_vmware_api_arguments,
)

