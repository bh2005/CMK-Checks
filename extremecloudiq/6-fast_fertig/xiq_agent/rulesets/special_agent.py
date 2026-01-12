#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (C) 2025 Your Company
# License: GNU General Public License v2

"""
WATO Ruleset for Extreme Cloud IQ Special Agent

This file defines the rule configuration interface for the special agent.

Install to: local/lib/python3/cmk_addons/plugins/xiq_agent/rulesets/special_agent.py
"""

from cmk.rulesets.v1 import Help, Title, Label
from cmk.rulesets.v1.form_specs import (
    CascadingSingleChoice,
    CascadingSingleChoiceElement,
    DefaultValue,
    DictElement,
    Dictionary,
    Integer,
    Password,
    String,
    validators,
)
from cmk.rulesets.v1.rule_specs import SpecialAgent, Topic

def _parameter_form_extreme_cloud_iq() -> Dictionary:
    """Define the parameter form for the special agent"""
    return Dictionary(
        title=Title("Extreme Cloud IQ Access Points"),
        help_text=Help(
            "Monitor Extreme Networks Access Points via Extreme Cloud IQ API. "
            "This special agent queries the Extreme Cloud IQ REST API to gather "
            "information about Access Points."
        ),
        elements={
            "authentication": DictElement(
                required=True,
                parameter_form=CascadingSingleChoice(
                    title=Title("Authentication Method"),
                    elements=[
                        CascadingSingleChoiceElement(
                            name="token",
                            title=Title("API Token"),
                            parameter_form=Dictionary(
                                elements={
                                    "token": DictElement(
                                        required=True,
                                        parameter_form=Password(
                                            title=Title("API Token"),
                                            help_text=Help("API Token generated in Extreme Cloud IQ"),
                                        ),
                                    ),
                                }
                            ),
                        ),
                        CascadingSingleChoiceElement(
                            name="credentials",
                            title=Title("Username and Password"),
                            parameter_form=Dictionary(
                                elements={
                                    "username": DictElement(
                                        required=True,
                                        parameter_form=String(title=Title("Username")),
                                    ),
                                    "password": DictElement(
                                        required=True,
                                        parameter_form=Password(title=Title("Password")),
                                    ),
                                }
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
                    prefill=DefaultValue(30),
                    label=Label("seconds"),
                ),
            ),
            "no_cert_check": DictElement(
                required=False,
                parameter_form=CascadingSingleChoice(
                    title=Title("SSL Certificate Verification"),
                    elements=[
                        CascadingSingleChoiceElement(
                            name="verify",
                            title=Title("Enable (recommended)"),
                            parameter_form=Dictionary(elements={}),
                        ),
                        CascadingSingleChoiceElement(
                            name="no_verify",
                            title=Title("Disable (insecure)"),
                            parameter_form=Dictionary(elements={}),
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
    topic=Topic.GENERAL,
    parameter_form=_parameter_form_extreme_cloud_iq,
)