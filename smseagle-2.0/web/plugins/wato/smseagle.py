#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# +-----------------------------------------------------------------------------------+
# |     _____   _____                                                                 |
# |    / __/ | / / _ |    Copyright   : (C) 2023 SVA System Vertrieb Alexander GmbH   |
# |   _\ \ | |/ / __ |    License     : GNU General Public License v2                 |
# |  /___/ |___/_/ |_|    Author      : Benedikt Bayer <benedikt.bayer@sva.de>        |
# |                                                                                   |
# +-----------------------------------------------------------------------------------+

from cmk.gui.valuespec import (
    TextAreaUnicode,
    TextAscii,
    Dictionary,
    ListOfStrings,
    Password,
)
from cmk.gui.i18n import _

default_host_content = """Host:     $HOSTNAME$
Alias:    $HOSTALIAS$
Event:    $EVENT_TXT$
Output:   $HOSTOUTPUT$"""
default_service_content = """Host:     $HOSTNAME$
Alias:    $HOSTALIAS$
Service:  $SERVICEDESC$
Event:    $EVENT_TXT$
Output:   $SERVICEOUTPUT$"""

register_notification_parameters(
    "smseagle",
    Dictionary(
        elements=[
            (
                "host",
                ListOfStrings(
                    allow_empty=False,
                    title=_("SMSEagle Gateways"),
                    help=_("Define one or multiple SMSEagle Gateways by hostname or ip."),
                ),
            ),
            (
                "username",
                TextAscii(title=_("Username"), help=_("Username for SMSEagle"), allow_empty=False),
            ),
            (
                "password",
                Password(title=_("Password"), help=_("Password for SMSEagle"), allow_empty=False),
            ),
            ("content_host",
             TextAreaUnicode(
                 title=_("Modify host notification content"),
                 rows=5,
                 cols=40,
                 monospaced=True,
                 default_value=default_host_content,
             )),
            ("content_service",
             TextAreaUnicode(
                 title=_("Modify service notification content"),
                 rows=5,
                 cols=40,
                 monospaced=True,
                 default_value=default_service_content,
             )),
        ],
        optional_keys=["content_host", "content_service"],
    ))
