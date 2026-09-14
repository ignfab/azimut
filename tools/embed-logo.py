#!/usr/bin/env python3
"""Produit azimut-autonome.html : une copie d'index.html avec le logo IGN
intégré en base64.

Utile pour distribuer un fichier unique, qui fonctionne même ouvert en double-clic
sans serveur web. Le reste de l'application est déjà autonome.

    python tools/embed-logo.py
"""
import base64
import mimetypes
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = ROOT / "index.html"
LOGO = ROOT / "assets" / "ign_logo.png"
DEST = ROOT / "azimut-autonome.html"

if not LOGO.exists():
    sys.exit(f"Logo introuvable : {LOGO}")

mime = mimetypes.guess_type(LOGO.name)[0] or "image/png"
data = base64.b64encode(LOGO.read_bytes()).decode("ascii")
uri = f"data:{mime};base64,{data}"

html = SRC.read_text(encoding="utf-8")
html, n = re.subn(
    r'const IGN_LOGO_URL = "[^"]*";',
    'const IGN_LOGO_URL = "' + uri + '";',
    html,
    count=1,
)
if n != 1:
    sys.exit("La constante IGN_LOGO_URL n'a pas ete trouvee dans index.html")

DEST.write_text(html, encoding="utf-8")
ko = len(data) / 1024
print(f"{DEST.name} ecrit — logo integre, {ko:.0f} Ko en base64")
