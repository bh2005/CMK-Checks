#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (C) 2025 bh2005
# License: GNU General Public License v2

"""
WATO Ruleset for Extreme Cloud IQ Special Agent

This file defines the rule configuration interface for the special agent.

Install to: local/lib/python3/cmk_addons/plugins/xiq_agent/rulesets/special_agent.py
"""

from cmk.rulesets.v1 import Help, Title, Label
from cmk.rulesets.v1.form_specs import (
    DefaultValue,
    DictElement,
    Dictionary,
    Integer,
    Password,
    SingleChoice,
    SingleChoiceElement,
    String,
    validators,
)
from cmk.rulesets.v1.rule_specs import SpecialAgent, Topic, Help, Title


def _parameter_form_extreme_cloud_iq() -> Dictionary:
    """Define the parameter form for the special agent"""
    return Dictionary(
        title=Title("Extreme Cloud IQ Access Points"),
        help_text=Help(
            "Monitor Extreme Networks Access Points via Extreme Cloud IQ API. "
            "This special agent queries the Extreme Cloud IQ REST API to gather "
            "information about Access Points, their connection status, client counts, "
            "and performance metrics."
        ),
        elements={
            "authentication": DictElement(
                required=True,
                parameter_form=SingleChoice(
                    title=Title("Authentication Method"),
                    help_text=Help(
                        "Choose how to authenticate with the Extreme Cloud IQ API. "
                        "API Token is recommended for production use."
                    ),
                    elements=[
                        SingleChoiceElement(
                            name="credentials",
                            title=Title("Username and Password"),
                            parameter_form=Dictionary(
                                elements={
                                    "username": DictElement(
                                        required=True,
                                        parameter_form=String(
                                            title=Title("Username"),
                                            help_text=Help(
                                                "Extreme Cloud IQ username (usually an email address)"
                                            ),
                                            custom_validate=(
                                                validators.LengthInRange(min_value=1),
                                            ),
                                        ),
                                    ),
                                    "password": DictElement(
                                        required=True,
                                        parameter_form=Password(
                                            title=Title("Password"),
                                            help_text=Help(
                                                "Password for the Extreme Cloud IQ user"
                                            ),
                                        ),
                                    ),
                                }
                            ),
                        ),
                        SingleChoiceElement(
                            name="token",
                            title=Title("API Token"),
                            parameter_form=Password(
                                title=Title("API Token"),
                                help_text=Help(
                                    "API Token generated in Extreme Cloud IQ "
                                    "(Global Settings → API Token Management). "
                                    "This is the recommended authentication method."
                                ),
                            ),
                        ),
                    ],
                    prefill=DefaultValue("token"),
                ),
            ),
            "timeout": DictElement(
                required=False,
                parameter_form=Integer(
                    title=Title("API Timeout"),
                    help_text=Help("Timeout in seconds for API requests"),
                    prefill=DefaultValue(30),
                    custom_validate=(
                        validators.NumberInRange(min_value=5, max_value=120),
                    ),
                    label=Label("seconds"),
                ),
            ),
            "no_cert_check": DictElement(
                required=False,
                parameter_form=SingleChoice(
                    title=Title("SSL Certificate Verification"),
                    help_text=Help(
                        "Enable or disable SSL certificate verification. "
                        "Disable only if using self-signed certificates (not recommended for production)"
                    ),
                    elements=[
                        SingleChoiceElement(
                            name="verify",
                            title=Title("Enable (recommended)"),
                        ),
                        SingleChoiceElement(
                            name="no_verify",
                            title=Title("Disable (insecure)"),
                        ),
                    ],
                    prefill=DefaultValue("verify"),
                ),
            ),
        },
    )


rule_spec_extreme_cloud_iq_special_agent = SpecialAgent(
    name="extreme_cloud_iq",
    title=Title("Extreme Cloud IQ Access Points"),
    topic=Topic.CLOUD,
    parameter_form=_parameter_form_extreme_cloud_iq,
)
