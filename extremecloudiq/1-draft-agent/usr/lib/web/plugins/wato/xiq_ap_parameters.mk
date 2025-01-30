from cmk.gui.i18n import _
from cmk.gui.valuespec import (
    Dictionary,
    Integer,
    Tuple,
    TextAscii,
)
from cmk.gui.plugins.wato import (
    rulespec_registry,
    HostRulespec,
)

def _valuespec_xiq_ap_parameters():
    return Dictionary(
        title=_("ExtremeCloud IQ AP Monitoring Parameters"),
        help=_("Configure thresholds for AP health, performance, and client metrics."),
        elements=[
            ("ap_status", Tuple(
                title=_("AP Status"),
                help=_("Set thresholds for AP status (Online/Offline)."),
                elements=[
                    Integer(title=_("Warning if offline for more than (minutes)"), default_value=5),
                    Integer(title=_("Critical if offline for more than (minutes)"), default_value=10),
                ],
            )),
            ("cpu_usage", Tuple(
                title=_("CPU Usage"),
                help=_("Set thresholds for AP CPU usage (percentage)."),
                elements=[
                    Integer(title=_("Warning if CPU usage exceeds (%)"), default_value=70),
                    Integer(title=_("Critical if CPU usage exceeds (%)"), default_value=90),
                ],
            )),
            ("memory_usage", Tuple(
                title=_("Memory Usage"),
                help=_("Set thresholds for AP memory usage (percentage)."),
                elements=[
                    Integer(title=_("Warning if memory usage exceeds (%)"), default_value=70),
                    Integer(title=_("Critical if memory usage exceeds (%)"), default_value=90),
                ],
            )),
            ("connected_clients", Tuple(
                title=_("Connected Clients"),
                help=_("Set thresholds for the number of connected clients."),
                elements=[
                    Integer(title=_("Warning if clients exceed"), default_value=50),
                    Integer(title=_("Critical if clients exceed"), default_value=100),
                ],
            )),
        ],
    )

rulespec_registry.register(
    HostRulespec(
        group="datasource_programs",
        name="xiq_ap_parameters",
        valuespec=_valuespec_xiq_ap_parameters,
    )
)