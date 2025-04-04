#!/usr/bin/env python3
# Shebang needed only for editors
from cmk.server_side_calls.v1 import noop_parser, SpecialAgentConfig, SpecialAgentCommand

def _agent_arguments(params, host_config):
    args = [
        "--username", params['user'],
        "--password", params['password'],
        "--xiq_base_url", params['xiq_base_url'],
        params['location_id']
    ]
    yield SpecialAgentCommand(command_arguments=args)

special_agent_xiq_wifi_health = SpecialAgentConfig(
    name="xiq_wifi_health",
    parameter_parser=noop_parser,
    commands_function=_agent_arguments
)