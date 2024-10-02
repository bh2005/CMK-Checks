#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# License: GNU General Public License v2
#
# Author: thl-cmk[at]outlook[dot]com
# URL   : https://thl-cmk.hopto.org
# Date  :
#
# 2023-02-21: moved from ~/local/share/check_mk/... to ~/local/lib/check_mk...
#

from cmk.gui.i18n import _
from cmk.gui.valuespec import (
    Dictionary,
    Tuple,
    TextAscii,
    ListOf,
    MonitoringState,
    TextUnicode,
)

from cmk.gui.plugins.wato.utils import (
    CheckParameterRulespecWithItem,
    rulespec_registry,
    RulespecGroupCheckParametersNetworking,
)


def _parameter_valuespec_cisco_wlc():
    return Dictionary(
        elements=[
            ('state_ap_missing',
             MonitoringState(
                 title=_('State if AP is missing'),
                 help=_('Set the monitoring state if the access point is not in the SNMP data. Default is WARN.'),
                 default_value=1,
             )),
            ('state_ap_change',
             MonitoringState(
                 title=_('State if H/W has changed'),
                 help=_('Set the monitoring state if the hard ware of the access point has changed. This information '
                        'will be used to help locate a missing access point '
                        'Default is WARN.'),
                 default_value=1,
             )),
            ('state_ap_offlinestatus',
             MonitoringState(
                 title=_('State if AP is not online'),
                 help=_('Default is WARN.'),
                 default_value=1,
             )),
            ('ap_list',
             ListOf(
                 Tuple(
                     elements=[
                         TextUnicode(
                             title=_('AP name'),
                             help=_('The configured value must match a AP item as reported by the monitored '
                                    'device. For example: "AP1.4"'),
                             allow_empty=False,
                             size=40,
                         ),
                         TextUnicode(
                             title=_('AP Alias'),
                             help=_('You can configure an individual alias here for the access point matching '
                                    'the text configured in the "AP item name" field. The alias will '
                                    'be shown in the check info'),
                             allow_empty=False,
                             size=40,
                         ),
                     ],
                     orientation='horizontal',
                 ),
                 title=_('AP alias'),
                 add_label=_('Add name'))),
            ('inv_ap_info', # added by plugin discovery function
             Dictionary(
                 title=_('Inventory AP Info'),
                 elements=[
                     ('ap_location', TextUnicode(title=_('Location'))),
                     ('ap_model', TextUnicode(title=_('Model'))),
                     ('ap_serialnumber', TextUnicode(title=_('Serial Number'))),
                     ('ap_ipaddress', TextUnicode(title=_('IP Address'))),
                     ('ap_mac_address', TextUnicode(title=_('MAC Address'))),
                     ('ap_host_name', TextUnicode(title=_('Hostname'))),
                     ('ap_version', TextUnicode(title=_('Version'))),
                     ('ap_rf_domain_name', TextUnicode(title=_('RF-Domain Name'))),
                     ('ap_online', TextUnicode(title=_('Online'))),
                 ],
             )),
        ],
        hidden_keys=['inv_ap_info'],
    )


rulespec_registry.register(
    CheckParameterRulespecWithItem(
        check_group_name='extreme_wlc',
        group=RulespecGroupCheckParametersNetworking,
        match_type='dict',
        parameter_valuespec=_parameter_valuespec_cisco_wlc,
        title=lambda: _('Extreme WLC APs'),
        item_spec=lambda: TextAscii(title=_('Extreme WLC AP name'), ),
    ))
