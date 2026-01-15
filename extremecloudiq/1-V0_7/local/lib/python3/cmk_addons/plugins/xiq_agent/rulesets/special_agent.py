# -*- coding: utf-8 -*-
# Dateipfad: ~/local/lib/python3/cmk_addons/plugins/xiq_agent/rulesets/special_agent.py

from cmk.rulesets.v1 import Title, Help
from cmk.rulesets.v1.form_specs import (
    DefaultValue,
    DictElement,
    Dictionary,
    migrate_to_password,
    Password,
    String,
    SingleChoice,
    SingleChoiceElement,
)
from cmk.rulesets.v1.rule_specs import SpecialAgent, Topic


def _parameter_form_xiq_agent():
    return Dictionary(
        title=Title("Extreme Cloud IQ"),
        help_text=Help(
            "Spezialagent fuer die Extreme Cloud IQ API. "
            "Holt Geraeteliste, Access Points und Client-Zahlen."
        ),
        elements={
            "url": DictElement(
                parameter_form=String(
                    title=Title("API Base URL"),
                    prefill=DefaultValue("https://api.extremecloudiq.com"),
                    help_text=Help("Normalerweise unveraendert lassen."),
                ),
            ),
            "username": DictElement(
                parameter_form=String(
                    title=Title("Username"),
                    help_text=Help("API-Benutzername (meist E-Mail)."),
                ),
            ),
            "password": DictElement(
                parameter_form=Password(
                    title=Title("Password"),
                    migrate=migrate_to_password,
                ),
            ),
            "no_cert_check": DictElement(
                parameter_form=SingleChoice(
                    title=Title("SSL-Zertifikatspruefung deaktivieren"),
                    elements=[
                        SingleChoiceElement(
                            name="no",
                            title=Title("Nein (empfohlen)"),
                        ),
                        SingleChoiceElement(
                            name="yes",
                            title=Title("Ja (nur fuer Tests)"),
                        ),
                    ],
                    help_text=Help(
                        "Aktivieren nur fuer Tests oder selbst-signierte Zertifikate. "
                        "In Produktion empfohlen: 'Nein'."
                    ),
                ),
            ),
        },
    )


rule_spec_special_agent_xiq_agent = SpecialAgent(
    name="xiq_agent",
    title=Title("Extreme Cloud IQ"),
    topic=Topic.GENERAL,
    parameter_form=_parameter_form_xiq_agent,
)