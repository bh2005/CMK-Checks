#!/usr/bin/env python3
# Shebang needed only for editors
from cmk.server_side_calls.v1 import noop_parser, SpecialAgentConfig, SpecialAgentCommand

def _agent_arguments(params, host_config):
    args = [
        "--username", params['user'],
        "--password", params['password'],
        "--xiq_base_url", params['xiq_base_url'],
    ]
    if params.get('views'):
        args.extend(["--views", params['views']])
    if params.get('page'):
        args.extend(["--page", str(params['page'])])
    if params.get('limit'):
        args.extend(["--limit", str(params['limit'])])
    if params.get('sort'):
        args.extend(["--sort", params['sort']])
    if params.get('dir'):
        args.extend(["--dir", params['dir']])
    if params.get('where'):
        args.extend(["--where", params['where']])
    yield SpecialAgentCommand(command_arguments=args)

special_agent_xiq_client_list = SpecialAgentConfig(
    name="xiq_client_list",
    parameter_parser=noop_parser,
    commands_function=_agent_arguments
)