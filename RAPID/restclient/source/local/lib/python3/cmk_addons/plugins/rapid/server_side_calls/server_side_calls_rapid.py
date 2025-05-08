# -*- encoding: utf-8; py-indent-offset: 4 -*-
#
# Server-side calls for RAPID Server Special Agent
# (c) 2025 Your Name <your.email@example.com>
# License: GNU General Public License v2
#
# Based on Checkmk Special Agent development guidelines

from typing import List
from cmk.base.plugins.agent_based.agent_based_api.v1 import (
    register,
    SpecialAgentCommand,
)

def generate_rapid_commands

(params: dict, hostname: str) -> List[SpecialAgentCommand]:
    """Generate command-line arguments for the RAPID Special Agent.

    Args:
        params: Dictionary with parameters from the ruleset (host, username, password, no_cert_check).
        hostname: Name of the host being monitored.

    Returns:
        List of SpecialAgentCommand objects with command-line arguments.
    """
    args = [
        "--host", params["host"],
        "--username", params["username"],
        "--password", params["password"],
    ]
    if params.get("no_cert_check", False):
        args.append("--no-cert-check")
    
    return [SpecialAgentCommand(command_arguments=args)]

register.special_agent(
    name="rapid",
    title="RAPID Server Special Agent",
    command_function=generate_rapid_commands,
)