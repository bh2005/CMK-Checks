#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ruleset-Konfiguration für den Defender for Endpoint Special Agent.
Ablage: ~/local/lib/python3/cmk_addons/plugins/defender_endpoint/rulesets/special_agent.py

Registriert den Agent unter: Setup > Agents > Other integrations
"""

from cmk.rulesets.v1 import Title, Help
from cmk.rulesets.v1.form_specs import (
    Dictionary,
    DictElement,
    String,
    Password,
    validators,
)
from cmk.rulesets.v1.rule_specs import SpecialAgent, Topic


def _formspec():
    return Dictionary(
        title=Title("Microsoft Defender for Endpoint"),
        help_text=Help(
            "Konfiguriert den Special Agent für Microsoft Defender for Endpoint (Digifant). "
            "Zugangsdaten kommen aus einer Azure App-Registrierung (Service Principal). "
            "Benötigte API-Berechtigung: WindowsDefenderATP → Alert.Read.All"
        ),
        elements={
            "tenant_id": DictElement(
                required=True,
                parameter_form=String(
                    title=Title("Azure Tenant ID"),
                    help_text=Help("Die Verzeichnis-ID (Tenant) aus der Azure App-Registrierung."),
                    custom_validate=(validators.LengthInRange(min_value=1),),
                ),
            ),
            "client_id": DictElement(
                required=True,
                parameter_form=String(
                    title=Title("Client ID (App-Registrierung)"),
                    help_text=Help("Die Anwendungs-ID (Client) der Azure App-Registrierung."),
                    custom_validate=(validators.LengthInRange(min_value=1),),
                ),
            ),
            "client_secret": DictElement(
                required=True,
                parameter_form=Password(
                    title=Title("Client Secret"),
                    help_text=Help("Das Client Secret aus der Azure App-Registrierung."),
                ),
            ),
        },
    )


rule_spec_defender_endpoint = SpecialAgent(
    topic=Topic.APPLICATIONS,
    name="defender_endpoint",
    title=Title("Microsoft Defender for Endpoint"),
    parameter_form=_formspec,
)