#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CheckMK 2.4 Ruleset for SMSEagle API v2 Notification Plugin

Uses the NEW Ruleset API v1 — compatible with CheckMK 2.4+.
The old cmk.gui.valuespec / cmk.gui.plugins.wato.utils approach
is deprecated since 2.3 and broken in 2.4.

Install to:
    local/lib/python3/cmk_addons/plugins/smseagle_api_v2/rulesets/ruleset_smseagle_api_v2.py

The notification script itself goes to:
    local/share/check_mk/notifications/smseagle_api_v2

NOTE: Do NOT re-register the 'pager' user attribute — it is a built-in
CheckMK field. Users configure their phone number / contact / group IDs
there directly.
"""

from cmk.rulesets.v1 import Help, Label, Title
from cmk.rulesets.v1.form_specs import (
    BooleanChoice,
    CascadingSingleChoice,
    CascadingSingleChoiceElement,
    DefaultValue,
    DictElement,
    Dictionary,
    FixedValue,
    Integer,
    MultilineText,
    Password,
    String,
    migrate_to_password,
)
from cmk.rulesets.v1.rule_specs import NotificationParameters, Topic


# ---------------------------------------------------------------------------
# Helper: individual form sections
# ---------------------------------------------------------------------------

def _primary_server_elements() -> dict:
    return {
        "primary_url": DictElement(
            parameter_form=String(
                title=Title("Primary SMSEagle URL"),
                help_text=Help(
                    "Base URL of your primary SMSEagle device. "
                    "Example: http://192.168.1.100  or  https://smseagle.company.com"
                ),
                prefill=DefaultValue("http://"),
            ),
            required=True,
        ),
        "primary_token": DictElement(
            parameter_form=Password(
                title=Title("Primary Access Token"),
                help_text=Help(
                    "API access token for the primary SMSEagle device. "
                    "Generate in SMSEagle web interface: Users → Access to API → Generate new token"
                ),
                migrate=migrate_to_password,
            ),
            required=True,
        ),
    }


def _secondary_server_elements() -> dict:
    return {
        "secondary_url": DictElement(
            parameter_form=String(
                title=Title("Secondary SMSEagle URL (Failover)"),
                help_text=Help(
                    "Optional: Base URL of your backup SMSEagle device. "
                    "Will be tried automatically if the primary device fails."
                ),
                prefill=DefaultValue("http://"),
            ),
            required=False,
        ),
        "secondary_token": DictElement(
            parameter_form=Password(
                title=Title("Secondary Access Token"),
                help_text=Help("API access token for the secondary/failover SMSEagle device."),
                migrate=migrate_to_password,
            ),
            required=False,
        ),
    }


def _message_type_element() -> dict:
    return {
        "message_type": DictElement(
            parameter_form=CascadingSingleChoice(
                title=Title("Message Type"),
                help_text=Help("Choose how the notification is delivered via SMSEagle."),
                elements=[
                    CascadingSingleChoiceElement(
                        name="sms",
                        title=Title("SMS Text Message"),
                        parameter_form=FixedValue(
                            value=None,
                            label=Label("Send notification as plain SMS"),
                        ),
                    ),
                    CascadingSingleChoiceElement(
                        name="call_tts",
                        title=Title("Voice Call — Text-to-Speech (TTS Advanced)"),
                        parameter_form=Integer(
                            title=Title("TTS Voice Model ID"),
                            help_text=Help(
                                "ID of the TTS voice model to use. "
                                "Check available models in SMSEagle under: Calls → TTS Voice models. "
                                "Common values: 1 = default English voice."
                            ),
                            prefill=DefaultValue(1),
                        ),
                    ),
                    CascadingSingleChoiceElement(
                        name="wave",
                        title=Title("Voice Call — WAV File"),
                        parameter_form=Integer(
                            title=Title("WAV File ID"),
                            help_text=Help(
                                "ID of the WAV file stored on the SMSEagle device. "
                                "Upload files under: Settings → Soundboard."
                            ),
                            prefill=DefaultValue(1),
                        ),
                    ),
                ],
                prefill=DefaultValue("sms"),
            ),
            required=True,
        ),
    }


def _modem_element() -> dict:
    return {
        "modem_no": DictElement(
            parameter_form=Integer(
                title=Title("Modem Number"),
                help_text=Help(
                    "Which modem slot to use for sending (1–4). "
                    "Check your SMSEagle hardware for the available number of modems."
                ),
                prefill=DefaultValue(1),
            ),
            required=False,
        ),
    }


def _ssl_element() -> dict:
    return {
        "verify_ssl": DictElement(
            parameter_form=BooleanChoice(
                title=Title("Verify SSL Certificate"),
                label=Label("Enable SSL certificate verification (recommended)"),
                help_text=Help(
                    "Disable only when using self-signed certificates. "
                    "Disabling this is a security risk — do not use in production."
                ),
                prefill=DefaultValue(True),
            ),
            required=False,
        ),
    }


def _template_element() -> dict:
    return {
        "message_template": DictElement(
            parameter_form=MultilineText(
                title=Title("Custom Message Template"),
                help_text=Help(
                    "Optional: Customise the notification message using CheckMK variables. "
                    "Leave empty to use the default format. "
                    "Available variables (without NOTIFY_ prefix, wrapped in $...$): "
                    "HOSTNAME, HOSTALIAS, HOSTADDRESS, HOSTSTATE, HOSTSHORTSTATE, HOSTOUTPUT, "
                    "SERVICEDESC, SERVICESTATE, SERVICESHORTSTATE, SERVICEOUTPUT, NOTIFICATIONTYPE. "
                    "Example: [$NOTIFICATIONTYPE$] $HOSTNAME$/$SERVICEDESC$ is $SERVICESTATE$: $SERVICEOUTPUT$"
                ),
                monospaced=True,
                prefill=DefaultValue(""),
            ),
            required=False,
        ),
    }


# ---------------------------------------------------------------------------
# Main form factory
# ---------------------------------------------------------------------------

def _notification_form() -> Dictionary:
    return Dictionary(
        title=Title("SMSEagle API v2 — Notification Settings"),
        help_text=Help(
            "Send CheckMK notifications via an SMSEagle hardware SMS gateway using API v2. "
            "Supports SMS, Text-to-Speech calls, and WAV-file calls. "
            "An optional secondary device can be configured as automatic failover."
        ),
        elements={
            **_primary_server_elements(),
            **_secondary_server_elements(),
            **_message_type_element(),
            **_modem_element(),
            **_ssl_element(),
            **_template_element(),
        },
    )


# ---------------------------------------------------------------------------
# Rule spec registration  (this is what CheckMK 2.4 discovers automatically)
# ---------------------------------------------------------------------------

rule_spec_smseagle_api_v2 = NotificationParameters(
    # 'name' must match the filename of the notification script
    # (local/share/check_mk/notifications/smseagle_api_v2)
    name="smseagle_api_v2",
    title=Title("SMSEagle API v2"),
    topic=Topic.NOTIFICATIONS,
    parameter_form=_notification_form,
)