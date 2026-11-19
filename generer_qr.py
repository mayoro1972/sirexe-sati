"""
Génère un QR code par commercial SATI + une carte A5 imprimable par commercial.

Usage :
    pip install "qrcode[pil]"
    python generer_qr.py https://mayoro1972.github.io/sirexe-sati/

Chaque QR pointe vers  <URL>?c=CODE  → le prospect est attribué au commercial.
Le QR "EQUIPE" pointe vers la même page sans attribution individuelle (flyers, kakemono).
Téléphone du commercial (mode agent, stockage hors-ligne) : <URL>?c=CODE&mode=agent
"""
import sys
from pathlib import Path
import qrcode
from qrcode.constants import ERROR_CORRECT_H
from PIL import Image, ImageDraw, ImageFont

BASE_URL = sys.argv[1] if len(sys.argv) > 1 else "https://mayoro1972.github.io/sirexe-sati/"
COMMERCIAUX = {  # garder identique à CONFIG.commerciaux dans index.html
    "SA01": "M. SIKA Ahui Jean Clément",
    "SA02": "M. KONAN Koffi Ange Parfait",
    "EQUIPE": "Équipe SATI",
}
NAVY = (20, 33, 61)
ORANGE = (232, 119, 46)
OUT = Path(__file__).parent / "qr"
OUT.mkdir(exist_ok=True)
try:
    FONT = ImageFont.truetype("/System/Library/Fonts/Avenir Next.ttc", 60, index=8)
except Exception:
    FONT = None


def make_qr(url):
    qr = qrcode.QRCode(error_correction=ERROR_CORRECT_H, box_size=20, border=2)
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color=NAVY, back_color="white").convert("RGB")
    w, _ = img.size
    r = w // 9
    d = ImageDraw.Draw(img)
    c = w // 2
    d.rounded_rectangle((c - r, c - r, c + r, c + r), radius=r // 3, fill="white")
    d.rounded_rectangle((c - r + 10, c - r + 10, c + r - 10, c + r - 10), radius=r // 4, fill=ORANGE)
    if FONT:
        d.text((c, c), "IA", fill="white", anchor="mm", font=FONT.font_variant(size=int(r * 0.9)))
    return img


sep = "&" if "?" in BASE_URL else "?"
cards = []
for code, nom in COMMERCIAUX.items():
    url = f"{BASE_URL}{sep}c={code}"
    make_qr(url).save(OUT / f"qr_{code}.png")
    cards.append((code, nom, url))
    print(f"{code:6} {nom:30} {url}")

html = """<!DOCTYPE html><html lang="fr"><head><meta charset="UTF-8">
<title>Cartes QR A5 — SATI · SIREXE 2026</title>
<style>
@page { size: A5; margin: 0 }
body { margin:0; font-family: -apple-system, Segoe UI, Roboto, Arial, sans-serif; background:#ddd }
.page { width:148mm; height:210mm; background:#fff; margin:10mm auto; page-break-after:always;
        display:flex; flex-direction:column; align-items:center; text-align:center; overflow:hidden }
.top { background:linear-gradient(135deg,#14213D,#2A3D66); color:#fff; width:100%; padding:10mm 8mm 8mm }
.top b { letter-spacing:.12em; font-size:11pt }
h1 { font-size:22pt; margin:4mm 0 2mm; line-height:1.1 }
h1 span { color:#F0A874 }
.top p { margin:0; font-size:11pt; color:#D5DAE4 }
img { width:84mm; margin:7mm 0 3mm }
.scan { font-weight:800; font-size:15pt; color:#14213D }
ul { list-style:none; padding:0; margin:3mm 0; font-size:10.5pt; color:#14213D }
.who { margin-top:auto; padding:4mm; font-size:9.5pt; color:#4C5466 }
@media print { body{background:#fff} .page{margin:0} }
</style></head><body>
"""
for code, nom, url in cards:
    html += f"""<div class="page">
  <div class="top"><b>SATI · HUB IA</b>
    <h1>Vos applications métier. <span>Avec l'IA dedans.</span></h1>
    <p>Hydrocarbures · Énergie · Mines — inscrite sur la plateforme Local Content</p></div>
  <img src="qr_{code}.png" alt="QR {code}">
  <div class="scan">📱 Scannez · 3 vidéos courtes</div>
  <ul><li>🛢️ Des applications pour vos sites</li><li>⚙️ L'IA dans vos processus, un par un</li><li>📅 Un rendez-vous de 45 minutes</li></ul>
  <div class="who">Votre commercial SATI : {nom} · réf. {code}<br>satiinformation@sati.ci · +225 07 07 39 12 42</div>
</div>
"""
html += "</body></html>"
(OUT / "cartes_A5.html").write_text(html, encoding="utf-8")
print("QR et cartes générés dans", OUT)
