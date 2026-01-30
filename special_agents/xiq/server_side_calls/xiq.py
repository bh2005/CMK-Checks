# -*- coding: utf-8 -*-
from typing import Iterator
from pydantic import BaseModel, Field
from cmk.server_side_calls.v1 import (
    SpecialAgentConfig,
    SpecialAgentCommand,
    HostConfig,
    Secret,
)

class XIQParams(BaseModel):
    url: str = Field(default="https://api.extremecloudiq.com")
    username: str
    password: Secret
    verify_tls: bool = True
    timeout: int = 30
    proxy_url: str | None = None

def _commands(params: XIQParams, host_config: HostConfig) -> Iterator[SpecialAgentCommand]:
    args: list[str] = [
        "--url", params.url,
        "--username", params.username,
        # Hier .unsafe() hinzufügen, um den Klartext zu übergeben:
        "--password", params.password.unsafe(), 
        "--timeout", str(params.timeout),
        "--host", host_config.name,
    ]
    if not params.verify_tls:
        args.append("--no-cert-check")
    if params.proxy_url:
        args += ["--proxy", params.proxy_url]
    yield SpecialAgentCommand(command_arguments=args)

special_agent_xiq = SpecialAgentConfig(
    name="xiq",
    parameter_parser=XIQParams.model_validate,
    commands_function=_commands,
)
