
# Link Dashlet (ZIP 0.1.2) – Checkmk 2.4.0p2 CEE

Dieses ZIP enthält die fertige Erweiterungsstruktur inkl. **Dashlet** und einer kleinen **CSS-Icon‑Library** (`skin/css/icons.css`).

## Inhalt
```
local/
  lib/python3/cmk_addons/plugins/gui/dashboard/dashlet/dashlets/link_dashlet.py
  share/check_mk/web/htdocs/skin/css/icons.css
  share/doc/link_dashlet/README.md
info
```

## Nutzung
**Variante A – direkt entpacken (lokaler Deploy)**
1. ZIP entpacken und den Ordner `local/` in deine Site kopieren (Pfad beibehalten).
2. `omd restart apache`

**Variante B – eigenes MKP erzeugen**
1. ZIP entpacken.
2. In den Elternordner `link_dashlet_0.1.2_zip/` wechseln (wo `info` und `local/` liegen).
3. `mkp pack . link-dashlet-0.1.2.mkp`
4. `mkp install link-dashlet-0.1.2.mkp && omd restart apache`

## Parameter-Hinweise
- **Icon mode**:
  - `theme` (empfohlen): `theme_icon_path` → z. B. `themes/modern-dark/images/myicon.svg`
  - `emoji`: `link_icon` → z. B. 📊
  - `custom`: `custom_icon_file` → z. B. `images/icons/my_icon.svg`
  - `css`: `icon_class` → z. B. `gg-dashboard` (stylesheet wird automatisch eingebunden)

## Theme-Icons (Option A)
Datei in dein aktives Theme legen und relativen Pfad im Dashlet setzen. Beispiel:
```bash
cp myicon.svg ~/local/share/check_mk/web/htdocs/themes/modern-dark/images/
omd restart apache
```

## Change Log
- 0.1.2 – ZIP-Distribution, CSS-Icons automatisch verlinkt, Doku aktualisiert
- 0.1.1 – MKP mit CSS-Icon-Placeholder
- 0.1.0 – Erstes MKP, kombiniertes Icon‑Konzept
