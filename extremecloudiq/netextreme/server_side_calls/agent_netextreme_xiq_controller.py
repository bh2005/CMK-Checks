#!/usr/bin/env python3
#-*- encoding: utf-8
#
# Author : Alexander Vogel (alexander.vogel.2305@gmail.com)
# Date   : 2025-11-28
# License: GNU General Public License v2
#
# Side Server Call: ExtremeCloud IQ Controller


from cmk.server_side_calls.v1 import HostConfig, Secret, SpecialAgentConfig, SpecialAgentCommand
from pydantic import BaseModel


class AgentNetextremeXiqController(BaseModel):
    port: int
    username: str
    password: Secret
    sections: list = None


def generate_netextreme_xiq_controller_command(params: AgentNetextremeXiqController, host_config: HostConfig):
    
    args = [
        "--server", host_config.primary_ip_config.address, 
        "--port", str(params.port), 
        "--username", params.username, 
        "--password", params.password.unsafe(),
    ]

    if params.sections is not None:
        args += ["--sections", ",".join(params.sections)]

    yield SpecialAgentCommand(command_arguments=args)


special_agent_netextreme_xiq_controller = SpecialAgentConfig(
    name="netextreme_xiq_controller",
    parameter_parser=AgentNetextremeXiqController.model_validate,
    commands_function=generate_netextreme_xiq_controller_command,
)