#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# License: GNU General Public License v2
#
# Author: thl-cmk[at]outlook[dot]com
# URL   : https://thl-cmk.hopto.org
# Date  : 2018-01-06
#
#
# missing a way to include hostname and service description
#
# 2023-02-21: moved from ~/local/share/check_mk/... to ~/local/lib/check_mk...
#
from cmk.gui.graphing import perfometer_info
from cmk.gui.graphing._utils import metric_info
from cmk.gui.i18n import _



#####################################################################################################################
#
# define metrics for perfdata
#
#####################################################################################################################

metric_info['extreme_wlc_uptime_seconds'] = {
    'title': _('AP uptime'),
    'help': _(''),
    'unit': 's',
    'color': '26/a',
}

######################################################################################################################
#
# define perf-o-meter
#
######################################################################################################################

perfometer_info.append(('stacked', [
    {
        'type': 'logarithmic',
        'metric': 'cisco_wlc_uptime_seconds',
        'half_value': 2592000.0,
        'exponent': 2,
    },
    {
        'type': 'linear',
        'segments': ['cisco_wlc_active_client_count'],
        'total': 200,
    }
]))
