#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from cmk.gui.i18n import _
from cmk.gui.valuespec import (
    Dictionary,
    TextInput,
    Password,
    DropdownChoice,
    Integer,
    ListOf,
    CascadingDropdown,
    FixedValue,
    Alternative,
)
from cmk.gui.plugins.wato.utils import (
    notification_parameter_registry,
    NotificationParameter,
)

@notification_parameter_registry.register
class NotificationParameterSMSEagle(NotificationParameter):
    @property
    def ident(self) -> str:
        return "smseagle"

    @property
    def spec(self) -> Dictionary:
        return Dictionary(
            title=_("SMSEagle SMS Notification (erweitert)"),
            help=_("Versand von Benachrichtigungen über SMSEagle API v2. Unterstützt SMS, Sprach-TTS-Anruf und WAV-Wiedergabe."),
            elements=[
                ("url", TextInput(
                    title=_("SMSEagle Basis-URL"),
                    help=_("z. B. https://192.168.1.100 oder http://smseagle.local"),
                    allow_empty=False,
                    size=50,
                )),
                ("auth_method", DropdownChoice(
                    title=_("Authentifizierung"),
                    choices=[
                        ("token", _("Access Token (empfohlen)")),
                        ("basic", _("Username + Password")),
                    ],
                    default_value="token",
                )),
                ("token", Password(
                    title=_("Access Token"),
                    allow_empty=False,
                )),
                ("username", TextInput(
                    title=_("Username (nur bei Basic Auth)"),
                )),
                ("password", Password(
                    title=_("Password (nur bei Basic Auth)"),
                )),
                ("message_type", DropdownChoice(
                    title=_("Nachrichtentyp"),
                    choices=[
                        ("sms", _("SMS")),
                        ("call_tts", _("Sprachanruf (Text-to-Speech)")),
                        ("wave", _("WAV-Datei abspielen")),
                    ],
                    default_value="sms",
                    help=_("Art der zu versendenden Nachricht"),
                )),
                ("text", TextInput(
                    title=_("Nachrichtentext"),
                    help=_("Pflichtfeld für SMS und TTS-Anruf. Wird in der Benachrichtigung verwendet (Platzhalter wie $HOSTNAME$, $OUTPUT$ möglich)."),
                    allow_empty=False,
                    size=80,
                )),
                ("wave_id", Integer(
                    title=_("WAV-Datei ID"),
                    help=_("ID der WAV-Datei im SMSEagle (nur bei Typ 'wave' erforderlich)"),
                    minvalue=1,
                )),
                ("modem_no", Integer(
                    title=_("Modem-Nummer"),
                    help=_("Welches Modem verwendet werden soll (Standard: 2)"),
                    default_value=2,
                    minvalue=1,
                    maxvalue=8,
                )),
                ("disable_ssl", DropdownChoice(
                    title=_("SSL-Zertifikatsprüfung deaktivieren"),
                    help=_("Unsicher! Nur bei selbstsignierten Zertifikaten aktivieren."),
                    choices=[
                        (False, _("Nein – Zertifikat prüfen")),
                        (True, _("Ja – Prüfung deaktivieren")),
                    ],
                    default_value=False,
                )),
                ("proxy", TextInput(
                    title=_("HTTP-Proxy (optional)"),
                    help=_("z. B. http://proxy.firma.de:8080"),
                    size=40,
                )),
                ("timeout", Integer(
                    title=_("API-Timeout (Sekunden)"),
                    default_value=15,
                    minvalue=5,
                    maxvalue=60,
                )),
            ],
            required_keys=["url", "token", "text"],  # Mindestens diese Felder
            optional_keys=["wave_id"],  # wave_id nur bei wave erforderlich – wir handhaben das im Script
            # Bedingte Sichtbarkeit über validate oder im Frontend (CMK macht das automatisch bei Cascading)
        )