#!/usr/bin/env python3
"""
WATO GUI Integration for ExtremeCloud IQ Special Agent

This provides:
1. Datasource program configuration in WATO
2. Rule configuration for check parameters
3. Nice GUI forms for all settings

Install to: local/lib/check_mk/gui/plugins/wato/
"""

from cmk.gui.i18n import _
from cmk.gui.valuespec import (
    Alternative,
    Dictionary,
    DropdownChoice,
    FixedValue,
    Float,
    Integer,
    Password,
    TextInput,
    Tuple,
)
from cmk.gui.plugins.wato.utils import (
    HostRulespec,
    rulespec_registry,
)
from cmk.gui.plugins.wato.datasource_programs import RulespecGroupDatasourceProgramsHardware
from cmk.gui.plugins.wato.check_parameters import (
    CheckParameterRulespecWithItem,
    CheckParameterRulespecWithoutItem,
    rulespec_registry,
)
from cmk.gui.plugins.wato.utils.simple_levels import SimpleLevels


# =============================================================================
# Datasource Program Configuration (Special Agent Rule)
# =============================================================================

def _valuespec_special_agents_extreme_cloud_iq():
    return Dictionary(
        title=_("ExtremeCloud IQ Access Points"),
        help=_(
            "Monitor Extreme Networks Access Points via ExtremeCloud IQ API. "
            "This special agent queries the ExtremeCloud IQ REST API to gather "
            "information about Access Points, their connection status, client counts, "
            "and performance metrics."
        ),
        elements=[
            (
                "auth_method",
                Alternative(
                    title=_("Authentication Method"),
                    help=_(
                        "Choose how to authenticate with the ExtremeCloud IQ API. "
                        "API Token is recommended for production use."
                    ),
                    elements=[
                        Dictionary(
                            title=_("Username and Password"),
                            elements=[
                                (
                                    "username",
                                    TextInput(
                                        title=_("Username"),
                                        help=_("ExtremeCloud IQ username (usually an email address)"),
                                        allow_empty=False,
                                        size=40,
                                    ),
                                ),
                                (
                                    "password",
                                    Password(
                                        title=_("Password"),
                                        help=_("Password for the ExtremeCloud IQ user"),
                                        allow_empty=False,
                                    ),
                                ),
                            ],
                            optional_keys=[],
                        ),
                        Dictionary(
                            title=_("API Token"),
                            elements=[
                                (
                                    "token",
                                    Password(
                                        title=_("API Token"),
                                        help=_(
                                            "API Token generated in ExtremeCloud IQ "
                                            "(Global Settings → API Token Management). "
                                            "This is the recommended authentication method."
                                        ),
                                        allow_empty=False,
                                        size=60,
                                    ),
                                ),
                            ],
                            optional_keys=[],
                        ),
                    ],
                    default_value={
                        "token": "",
                    },
                ),
            ),
            (
                "timeout",
                Integer(
                    title=_("API Timeout"),
                    help=_("Timeout in seconds for API requests"),
                    default_value=30,
                    minvalue=5,
                    maxvalue=120,
                    unit=_("seconds"),
                ),
            ),
            (
                "debug",
                DropdownChoice(
                    title=_("Debug Mode"),
                    help=_(
                        "Enable debug output in agent execution. "
                        "Debug information will be written to ~/var/log/agent-output/"
                    ),
                    choices=[
                        (False, _("Disabled")),
                        (True, _("Enabled")),
                    ],
                    default_value=False,
                ),
            ),
        ],
        optional_keys=["timeout", "debug"],
    )


rulespec_registry.register(
    HostRulespec(
        group=RulespecGroupDatasourceProgramsHardware,
        name="special_agents:extreme_cloud_iq",
        valuespec=_valuespec_special_agents_extreme_cloud_iq,
    )
)


# =============================================================================
# Check Parameter Rules
# =============================================================================

# Rule 1: AP Clients Thresholds
def _parameter_valuespec_extreme_ap_clients():
    return Dictionary(
        title=_("ExtremeCloud IQ AP Client Count Levels"),
        help=_(
            "Configure warning and critical levels for the number of clients "
            "connected to an Access Point. High client counts may indicate "
            "overloaded APs or the need for additional coverage."
        ),
        elements=[
            (
                "clients_warn",
                Integer(
                    title=_("Warning at"),
                    help=_("Number of clients that triggers a WARNING state"),
                    default_value=50,
                    minvalue=1,
                    unit=_("clients"),
                ),
            ),
            (
                "clients_crit",
                Integer(
                    title=_("Critical at"),
                    help=_("Number of clients that triggers a CRITICAL state"),
                    default_value=80,
                    minvalue=1,
                    unit=_("clients"),
                ),
            ),
        ],
        optional_keys=[],
    )


rulespec_registry.register(
    CheckParameterRulespecWithoutItem(
        check_group_name="extreme_ap_clients",
        group=RulespecGroupCheckParametersNetworking,
        match_type="dict",
        parameter_valuespec=_parameter_valuespec_extreme_ap_clients,
        title=lambda: _("ExtremeCloud IQ AP Client Count"),
    )
)


# Rule 2: AP Details (CPU, Memory)
def _parameter_valuespec_extreme_ap_details():
    return Dictionary(
        title=_("ExtremeCloud IQ AP Performance Levels"),
        help=_(
            "Configure thresholds for Access Point CPU and memory utilization. "
            "High values may indicate performance issues or the need for maintenance."
        ),
        elements=[
            (
                "cpu_warn",
                Float(
                    title=_("CPU Warning Level"),
                    help=_("CPU utilization percentage that triggers a WARNING"),
                    default_value=80.0,
                    minvalue=0.0,
                    maxvalue=100.0,
                    unit="%",
                ),
            ),
            (
                "cpu_crit",
                Float(
                    title=_("CPU Critical Level"),
                    help=_("CPU utilization percentage that triggers a CRITICAL"),
                    default_value=90.0,
                    minvalue=0.0,
                    maxvalue=100.0,
                    unit="%",
                ),
            ),
            (
                "memory_warn",
                Float(
                    title=_("Memory Warning Level"),
                    help=_("Memory utilization percentage that triggers a WARNING"),
                    default_value=80.0,
                    minvalue=0.0,
                    maxvalue=100.0,
                    unit="%",
                ),
            ),
            (
                "memory_crit",
                Float(
                    title=_("Memory Critical Level"),
                    help=_("Memory utilization percentage that triggers a CRITICAL"),
                    default_value=90.0,
                    minvalue=0.0,
                    maxvalue=100.0,
                    unit="%",
                ),
            ),
        ],
        optional_keys=[],
    )


rulespec_registry.register(
    CheckParameterRulespecWithoutItem(
        check_group_name="extreme_ap_details",
        group=RulespecGroupCheckParametersNetworking,
        match_type="dict",
        parameter_valuespec=_parameter_valuespec_extreme_ap_details,
        title=lambda: _("ExtremeCloud IQ AP Performance"),
    )
)


# =============================================================================
# Additional Helper: Host Tag for AP Types (Optional)
# =============================================================================

# This allows you to create host tags for different AP types/locations
# and apply different thresholds based on those tags

"""
To use this, add to local/lib/check_mk/gui/plugins/wato/tags.py:

from cmk.gui.plugins.wato import (
    HostTagGroup,
    HostTagGroupSpec,
)

register_hosttag_group(
    HostTagGroupSpec(
        id="extreme_ap_type",
        title="Extreme AP Type",
        tags=[
            ("indoor", "Indoor AP", []),
            ("outdoor", "Outdoor AP", []),
            ("high_density", "High Density AP", []),
        ],
    )
)
"""


# =============================================================================
# Agent Bakery Integration (Optional - for CMK Enterprise)
# =============================================================================

try:
    from cmk.gui.cee.plugins.bakery.bakery_api.v1 import (
        FileGenerator,
        Plugin,
        PluginConfig,
        register,
    )

    def get_extreme_cloud_iq_plugin_files(conf):
        """Generate agent plugin files for ExtremeCloud IQ"""
        if not conf:
            return

        # Build command line arguments
        args = []
        
        auth = conf.get("auth_method", {})
        if "token" in auth:
            args.append(f"--api-token {auth['token']}")
        elif "username" in auth and "password" in auth:
            args.append(f"--username {auth['username']}")
            args.append(f"--password {auth['password']}")
        
        if conf.get("timeout"):
            args.append(f"--timeout {conf['timeout']}")
        
        if conf.get("debug"):
            args.append("--debug")
        
        command = f"agent_extreme_cloud_iq {' '.join(args)}"
        
        yield Plugin(
            base_os="linux",
            source=FileGenerator(
                "extreme_cloud_iq",
                command,
            ),
        )

    register.bakery_plugin(
        name="extreme_cloud_iq",
        files_function=get_extreme_cloud_iq_plugin_files,
    )

except ImportError:
    # Agent Bakery not available (Raw Edition)
    pass