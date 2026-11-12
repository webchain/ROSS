"""Bouwt de Shopify-import voor de ROSS-demowinkel uit de publieke productfeed.

Gebruik:  python3 build_import.py <products.json> <uitvoermap>

Uitvoer:
  producten-import.csv   Shopify product-CSV (nieuwe kolomnamen) met metafield-kolommen
  koffievelden.csv       Overzicht per koffie, om na te kijken
  rapport.md             Wat er is opgekuist, weggelaten en nagekeken moet worden
"""
import csv
import html
import json
import re
import sys
from pathlib import Path

from bs4 import BeautifulSoup, Comment

# ---------------------------------------------------------------- instellingen

WEGLATEN = {"test", "digital-product-2"}  # testproduct en lege "Digital product" van 0 euro

REGIO_KLEUR = {
    "Huisblend": "#7B4B2A",
    "Afrika": "#F07D1F",
    "Midden-Amerika": "#D3302B",
    "Zuid-Amerika": "#B22A6E",
    "Azië": "#CDAA21",
    "Cafeïnevrij": "#6E6E6E",
}
LAND_REGIO = {
    "burundi": "Afrika", "uganda": "Afrika", "rwanda": "Afrika", "tanzania": "Afrika",
    "kenya": "Afrika", "ethiopia": "Afrika", "ethiopië": "Afrika", "cameroon": "Afrika",
    "el salvador": "Midden-Amerika", "costa rica": "Midden-Amerika", "honduras": "Midden-Amerika",
    "mexico": "Midden-Amerika", "guatemala": "Midden-Amerika",
    "colombia": "Zuid-Amerika", "peru": "Zuid-Amerika", "brazil": "Zuid-Amerika",
    "china": "Azië", "indonesia": "Azië",
}

# metafield: (kolomnaam, sleutel, type) — type staat in de definitielijst
METAFIELDS = [
    ("Koffienaam", "koffienaam", "single_line_text_field"),
    ("Nummer filter", "nummer_filter", "number_integer"),
    ("Nummer espresso", "nummer_espresso", "number_integer"),
    ("Regio", "regio", "single_line_text_field"),
    ("Labelkleur", "labelkleur", "color"),
    ("Smaaknotities", "smaaknotities", "single_line_text_field"),
    ("Herkomst", "herkomst", "multi_line_text_field"),
    ("Variëteit en verwerking", "verwerking", "multi_line_text_field"),
    ("Waarom bijzonder", "waarom", "multi_line_text_field"),
    ("Oogstperiode", "oogst", "single_line_text_field"),
    ("Tips", "tips", "multi_line_text_field"),
]

OPTIE_TOESTEL, OPTIE_GEWICHT, OPTIE_MALING = "Toestel", "Gewicht", "Maling"

EMOJI = re.compile(
    "[\U0001F000-\U0001FAFF\U0001F1E6-\U0001F1FF☀-➿⬀-⯿️‍⃣]"
)

# ---------------------------------------------------------------- hulpfuncties


def zonder_emoji(s):
    return re.sub(r"[ \t]{2,}", " ", EMOJI.sub("", s or "")).strip()


def opgekuiste_html(body):
    """Emoji, inline stijlen, klassen, data-attributen, svg's en lege tags weg."""
    if not body:
        return ""
    soup = BeautifulSoup(body, "html.parser")
    for c in soup.find_all(string=lambda t: isinstance(t, Comment)):
        c.extract()
    for t in soup.find_all(["svg", "script", "style"]):
        t.decompose()
    for t in soup.find_all(True):
        keep = {}
        if t.name == "a" and t.get("href"):
            keep["href"] = t["href"]
        t.attrs = keep
    for t in soup.find_all(["span", "div", "section"]):
        t.unwrap()
    for t in soup.find_all(string=True):
        nieuw = EMOJI.sub("", t)
        if nieuw != t:
            t.replace_with(nieuw)
    changed = True
    while changed:
        changed = False
        for t in soup.find_all(["p", "strong", "b", "a", "li", "ul", "h2", "h3", "blockquote"]):
            if not t.get_text(strip=True) and not t.find("img"):
                t.decompose()
                changed = True
    out = str(soup)
    out = re.sub(r"(<br/?>\s*){2,}", "<br/>", out)
    out = re.sub(r"\n{2,}", "\n", out)
    return out.strip()


INLINE_KOPPEN = re.compile(
    r"(Waarom deze (?:koffie|blend) bijzonder is|De regio[’']?s? &(?:amp;)? bijzonderheden|Oogstperiodes?\b)"
)


def tekstregels(body):
    h = body or ""
    h = re.sub(r"(?i)<br\s*/?>", "\n", h)
    h = re.sub(r"(?i)</(p|li|h\d|div|ul)>", "\n", h)
    h = re.sub(r"(?i)<hr\s*/?>", "\n---\n", h)
    h = re.sub(r"<[^>]+>", "", h)
    h = html.unescape(h).replace("\xa0", " ")
    # koppen die zonder regeleinde aan de tekst plakken, op een eigen regel zetten
    h = INLINE_KOPPEN.sub(lambda m: "\n" + m.group(1) + "\n", h)
    h = re.sub(r"\s*(👉|💡)", r"\n\1", h)
    return [r.strip() for r in h.split("\n") if r.strip()]


KOPPEN = ("smaakpatroon", "discover the taste", "herkomst", "variëteit", "samenstelling",
          "waarom deze", "de regio", "kleine telers", "kleine boeren", "oogstperiode",
          "het swiss water", "wanneer drink", "---")
TIP_START = ("perfect voor", "ideaal", "combineert", "heerlijk als", "aanrader", "veelzijdig")


def is_echte_kop(regel):
    return zonder_emoji(regel).lower().startswith(KOPPEN) or regel.startswith(("💡", "👉"))


def is_tussentitel(regel):
    # korte regel zonder eindpunt = tussentitel ("Kleine telers, rijke traditie")
    r = zonder_emoji(regel)
    return len(r) < 60 and not r.endswith((".", "!", "?", ":"))


def sectie(regels, starts, na_kop=True, stop_bij_tussentitel=False, max_regels=None):
    """Regels na de eerste kop die met een van `starts` begint, tot de volgende kop."""
    if isinstance(starts, str):
        starts = (starts,)
    for i, r in enumerate(regels):
        if zonder_emoji(r).lower().startswith(starts):
            rest = r.split(":", 1)[1].strip() if ":" in r and na_kop else ""
            out = [rest] if rest else []
            for r2 in regels[i + 1:]:
                if is_echte_kop(r2) or (stop_bij_tussentitel and out and is_tussentitel(r2)):
                    break
                out.append(r2)
                if max_regels and len(out) >= max_regels:
                    break
            return out
    return []


def splits_aaneen(s):
    """Beschrijvingen zonder regeleinden: 'Yunnan, China1.400' -> twee regels."""
    s = s.replace("•", "\n")
    s = re.sub(r"(?<=[a-zà-ÿ\)])(?=\d)", "\n", s)
    s = re.sub(r"(?<=[a-zà-ÿ\)])(?=[A-Z])", "\n", s)
    return "\n".join(x.strip(" –-") for x in s.split("\n") if x.strip(" –-"))


def koffievelden(p):
    regels = tekstregels(p["body_html"])
    m = re.match(r"^\s*(\d+)\s*/\s*(\d+)\s+(.*)$", p["title"])
    naam = re.sub(r"\s{2,}", " ", (m.group(3) if m else p["title"])).strip()
    tags = [t.lower() for t in p["tags"]]
    if p["product_type"] == "Blends" and m:
        regio = "Huisblend"
    elif "deca" in tags or p["handle"].startswith("specialty-coffee-decaf"):
        regio, naam = "Cafeïnevrij", "Deca"
    else:
        regio = ""
        zoek = " ".join(tags) + " " + naam.lower()
        for land, r in LAND_REGIO.items():
            if land in zoek:
                regio = r
                break
    smaak = sectie(regels, ("smaakpatroon", "discover the taste"), max_regels=1)
    scheiding = "|" if "|" in " ".join(smaak) else ","
    noten = [zonder_emoji(x) for x in " | ".join(smaak).split(scheiding)]
    noten = [n[:1].upper() + n[1:] for n in noten if n]
    herkomst = splits_aaneen("\n".join(zonder_emoji(x) for x in sectie(regels, "herkomst")))
    verwerking = splits_aaneen("\n".join(zonder_emoji(x) for x in sectie(regels, ("variëteit", "samenstelling"))))
    waarom = "\n".join(zonder_emoji(x) for x in
                       sectie(regels, "waarom deze", na_kop=False, stop_bij_tussentitel=True))
    oogst_regels = []
    for x in splits_aaneen("\n".join(sectie(regels, "oogstperiode", na_kop=False))).split("\n"):
        x = zonder_emoji(x)
        if x.lower().startswith(TIP_START) or len(x) > 70:
            break
        if x and not x.startswith("("):
            oogst_regels.append(x.rstrip(":"))
    oogst = " · ".join(oogst_regels)
    # tips: regels met 💡/👉, plus losse regels die met een zet- of combinatietip beginnen
    tips, bezig = [], False
    for r in regels:
        if r.startswith(("💡", "👉")):
            bezig = True
        elif is_echte_kop(r):
            bezig = False
        if bezig or zonder_emoji(r).lower().startswith(TIP_START):
            t = zonder_emoji(r)
            if t and t not in tips:
                if tips and tips[-1].endswith(":"):
                    tips[-1] = tips[-1] + " " + t
                else:
                    tips.append(t)
    tips = "\n".join(tips)
    spatie = lambda s: re.sub(r"(?<=[a-z’'\)])\.(?=[A-Z])", ". ", s)
    waarom, tips = spatie(waarom), spatie(tips)
    return {
        "koffienaam": naam,
        "nummer_filter": m.group(1) if m else "",
        "nummer_espresso": m.group(2) if m else "",
        "regio": regio,
        "labelkleur": REGIO_KLEUR.get(regio, ""),
        "smaaknotities": " | ".join(noten),
        "herkomst": herkomst.strip(),
        "verwerking": verwerking.strip(),
        "waarom": waarom.strip(),
        "oogst": oogst.strip(),
        "tips": tips.strip(),
    }


def is_koffie(p):
    if p["product_type"] == "Single origins":
        return True
    return p["product_type"] == "Blends" and re.match(r"^\s*\d+\s*/\s*\d+", p["title"])


def norm_gewicht(v):
    s = v.lower().replace(" ", "")
    if s in ("250g", "250gr"):
        return "250 g"
    if s in ("1kg", "1000gr", "1000g"):
        return "1 kg"
    m = re.match(r"^(\d)(x1kg|kg)$", s)
    if m:
        return f"{m.group(1)} kg"
    return v


def optie_naam(naam, waarden):
    w = {x.lower() for x in waarden}
    if w <= {"espresso", "filter"}:
        return OPTIE_TOESTEL
    if w <= {"bonen", "gemalen"}:
        return OPTIE_MALING
    if naam.lower() == "gewicht":
        return OPTIE_GEWICHT
    return naam


def bool_s(b):
    return "true" if b else "false"


# ---------------------------------------------------------------- hoofdprogramma


def main(src, outdir):
    producten = json.load(open(src, encoding="utf-8"))["products"]
    outdir = Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    opties = [f"Option{i} {k}" for i in (1, 2, 3) for k in ("name", "value", "LinkedTo")]
    kolommen = (["Title", "URL handle", "Description", "Vendor", "Type", "Tags",
                 "Published on online store", "Status", "SKU"]
                + opties
                + ["Price", "Compare-at price", "Charge tax", "Inventory tracker", "Inventory quantity",
                   "Weight value (grams)", "Weight unit for display", "Requires shipping",
                   "Product image URL", "Image position", "Image alt text", "Variant image URL"]
                + [f"{label} (product.metafields.custom.{key})" for label, key, _ in METAFIELDS])
    # LinkedTo-kolommen laten we leeg; ze zijn optioneel
    rijen, overzicht, rapport = [], [], []
    weggelaten = []

    for p in producten:
        if p["handle"] in WEGLATEN:
            weggelaten.append(p["title"])
            continue
        velden = koffievelden(p) if is_koffie(p) else {}
        optiedef = [(optie_naam(o["name"], o["values"]), o["name"]) for o in p["options"]]
        afbeeldingen = [i["src"].split("?")[0] for i in p["images"]]
        alt = {i["src"].split("?")[0]: (i.get("alt") or "") for i in p["images"]}

        for vi, v in enumerate(p["variants"]):
            r = {k: "" for k in kolommen}
            r["URL handle"] = p["handle"]
            if vi == 0:
                r.update({
                    "Title": p["title"].strip(),
                    "Description": opgekuiste_html(p["body_html"]),
                    "Vendor": p["vendor"],
                    "Type": p["product_type"],
                    "Tags": ", ".join(p["tags"]),
                    "Published on online store": "true",
                    "Status": "active",
                })
                for label, key, _ in METAFIELDS:
                    r[f"{label} (product.metafields.custom.{key})"] = velden.get(key, "")
            for oi, (nieuw, oud) in enumerate(optiedef, start=1):
                waarde = v.get(f"option{oi}") or ""
                if nieuw == OPTIE_GEWICHT:
                    waarde = norm_gewicht(waarde)
                if vi == 0:
                    r[f"Option{oi} name"] = nieuw
                r[f"Option{oi} value"] = waarde
            r.update({
                "SKU": v.get("sku") or "",
                "Price": v["price"],
                "Compare-at price": v["compare_at_price"] if v.get("compare_at_price") not in (None, "0.00") else "",
                "Charge tax": bool_s(v["taxable"]),
                "Inventory tracker": "shopify",
                "Inventory quantity": "25" if v["available"] else "0",
                "Weight value (grams)": str(v.get("grams") or 0),
                "Weight unit for display": "g",
                "Requires shipping": bool_s(v["requires_shipping"]),
                "Variant image URL": (v.get("featured_image") or {}).get("src", "").split("?")[0],
            })
            if vi < len(afbeeldingen):
                r["Product image URL"] = afbeeldingen[vi]
                r["Image position"] = str(vi + 1)
                r["Image alt text"] = alt.get(afbeeldingen[vi], "")
            rijen.append(r)
        # extra afbeeldingen als losse rijen
        for ii in range(len(p["variants"]), len(afbeeldingen)):
            r = {k: "" for k in kolommen}
            r["URL handle"] = p["handle"]
            r["Product image URL"] = afbeeldingen[ii]
            r["Image position"] = str(ii + 1)
            r["Image alt text"] = alt.get(afbeeldingen[ii], "")
            rijen.append(r)

        if velden:
            overzicht.append({"handle": p["handle"], "titel": p["title"].strip(), **velden})
            leeg = [k for k in ("regio", "smaaknotities", "herkomst", "waarom") if not velden.get(k)]
            if leeg:
                rapport.append(f"- {p['title'].strip()}: niet gevonden in de beschrijving: {', '.join(leeg)}")
        hernoemd = [f"{o} → {n}" for n, o in optiedef if n != o]
        if hernoemd:
            rapport.append(f"- {p['title'].strip()}: opties hernoemd ({'; '.join(hernoemd)})")

    with open(outdir / "producten-import.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=kolommen)
        w.writeheader()
        w.writerows(rijen)
    with open(outdir / "koffievelden.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(overzicht[0].keys()))
        w.writeheader()
        w.writerows(overzicht)

    n_prod = len(producten) - len(weggelaten)
    with open(outdir / "rapport.md", "w", encoding="utf-8") as f:
        f.write("# Rapport productimport\n\n")
        f.write(f"- Producten in de feed: {len(producten)}\n- Geïmporteerd: {n_prod}\n")
        f.write(f"- Weggelaten (testproducten): {', '.join(weggelaten)}\n")
        f.write(f"- Koffies met koffievelden: {len(overzicht)}\n- CSV-rijen: {len(rijen)}\n\n")
        f.write("## Na te kijken\n\n" + ("\n".join(rapport) if rapport else "Niets.") + "\n")
    print(f"{n_prod} producten, {len(overzicht)} koffies, {len(rijen)} rijen")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
