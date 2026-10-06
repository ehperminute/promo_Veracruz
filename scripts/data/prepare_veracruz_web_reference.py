from pathlib import Path
import re

import pandas as pd
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data" / "raw"
REF = ROOT / "data" / "reference"
OUTDIR = ROOT / "data" / "interim"

PRODUCTS_HTML = RAW / "veracruz_productos_2026-10-06.html"
REGIONS_HTML = RAW / "veracruz_regiones_2026-10-06.html"
PUEBLOS_HTML = RAW / "veracruz_pueblos_magicos_2026-10-06.html"
PUEBLOS_MANUAL_HTML = RAW / "veracruz_pueblos_magicos_2026-10-06_manual.html"
ALIASES = REF / "web_name_aliases.csv"

PRODUCTS_OUT = OUTDIR / "veracruz_products_parsed.csv"
REGIONS_OUT = OUTDIR / "veracruz_regions_parsed.csv"
PUEBLOS_OUT = OUTDIR / "veracruz_pueblos_magicos_parsed.csv"

REGION_CANONICAL = {
    "Huasteca": "Huasteca",
    "Totonacapan": "Totonacapan",
    "Cultura y Aventura": "Cultura y Aventura",
    "Primeros pasos de Cortés": "Primeros Pasos de Cortés",
    "Altas montañas": "Altas Montañas",
    "Los Tuxtlas": "Los Tuxtlas",
    "Olmeca": "Olmeca",
}


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def _aliases() -> dict[tuple[str, str], str]:
    df = pd.read_csv(ALIASES)
    return {
        (str(r.context), str(r.source_name)): str(r.canonical_name)
        for r in df.itertuples(index=False)
    }


def _canonical_name(name: str, context: str, aliases: dict[tuple[str, str], str]) -> str:
    name = re.sub(r"\s+", " ", str(name)).strip(" ;,.\t\r\n")
    return aliases.get((context, name), name)


def _split_municipalities(value: str, aliases: dict[tuple[str, str], str]) -> list[str]:
    # The source uses semicolons plus Spanish conjunction "y" for the final item.
    value = re.sub(r"\s+y\s+", ";", value.strip())
    parts = [p.strip(" ;,.\t\r\n") for p in value.split(";") if p.strip()]
    return [_canonical_name(p, "product_municipality", aliases) for p in parts]


def parse_products() -> pd.DataFrame:
    aliases = _aliases()
    soup = BeautifulSoup(_text(PRODUCTS_HTML), "html.parser")
    rows = []
    for idx, card in enumerate(soup.select(".info-card-header"), start=1):
        h1 = card.find("h1")
        h3 = card.find("h3")
        if not h1 or not h3:
            continue
        product = re.sub(r"\s+", " ", h1.get_text(" ", strip=True)).strip()
        municipalities = _split_municipalities(h3.get_text(" ", strip=True), aliases)
        if not product or not municipalities:
            continue
        rows.append(
            {
                "source_card_index": idx,
                "producto": product,
                "municipios": "|".join(municipalities),
                "n_municipios": len(set(municipalities)),
                "source_snapshot": str(PRODUCTS_HTML.relative_to(ROOT)),
            }
        )
    out = pd.DataFrame(rows)
    if len(out) < 250:
        raise AssertionError(f"Products parser found unexpectedly few cards: {len(out)}")
    return out


def parse_regions() -> pd.DataFrame:
    aliases = _aliases()
    soup = BeautifulSoup(_text(PRODUCTS_HTML), "html.parser")
    rows = []
    seen_regions = set()
    for a in soup.find_all("a", href=True):
        href = a.get("href", "")
        if not re.fullmatch(r"region\.php\?id=\d+", href):
            continue
        raw_region = re.sub(r"\s+", " ", a.get_text(" ", strip=True)).strip()
        if raw_region == "Mostrar Todos" or raw_region not in REGION_CANONICAL:
            continue
        region = REGION_CANONICAL[raw_region]
        if region in seen_regions:
            continue
        seen_regions.add(region)
        ul = a.find_next_sibling("ul")
        if ul is None:
            raise AssertionError(f"Region menu has no municipality list: {raw_region}")
        for child in ul.find_all("a"):
            chref = child.get("href", "")
            match = re.fullmatch(r"destino\.php\?Municipio=(\d+)", chref)
            if not match:
                continue
            source_name = re.sub(r"\s+", " ", child.get_text(" ", strip=True)).strip()
            canonical = _canonical_name(source_name, "region_municipality", aliases)
            mun_id = int(match.group(1))
            rows.append(
                {
                    "region": region,
                    "source_municipality_name": source_name,
                    "municipio": canonical,
                    "source_municipio_id": mun_id,
                    "clave_municipio": f"30{mun_id:03d}",
                    "source_snapshot": str(PRODUCTS_HTML.relative_to(ROOT)),
                }
            )
    out = pd.DataFrame(rows)
    if set(out["region"].unique()) != set(REGION_CANONICAL.values()):
        raise AssertionError(f"Expected 7 tourism regions, got {sorted(out['region'].unique())}")
    if out["clave_municipio"].duplicated().any():
        dupes = out[out["clave_municipio"].duplicated(False)]
        raise AssertionError(f"Region menu maps municipality code more than once:\n{dupes}")
    # Keep the separately downloaded region page as source evidence and verify it is a real page.
    region_html = _text(REGIONS_HTML)
    if "Regiones Turísticas" not in region_html or "El Estado de Veracruz se divide en 7 Regiones Turísticas" not in region_html:
        raise AssertionError("Frozen regions snapshot does not look like the expected official region page")
    return out.sort_values(["region", "clave_municipio"], kind="stable").reset_index(drop=True)


def parse_pueblos_magicos() -> pd.DataFrame:
    aliases = _aliases()

    # Preferred source: a browser-saved copy of the real SECTUR page. The
    # automated Codespaces request is preserved separately because it returned
    # a Radware CAPTCHA challenge.
    if PUEBLOS_MANUAL_HTML.is_file():
        manual_html = _text(PUEBLOS_MANUAL_HTML)
        manual_soup = BeautifulSoup(manual_html, "html.parser")
        iframe_names = []
        for iframe in manual_soup.select("article iframe[title]"):
            raw_name = re.sub(r"\s+", " ", iframe.get("title", "")).strip()
            if raw_name:
                iframe_names.append(raw_name)
        names = list(dict.fromkeys(iframe_names))
        if len(names) == 8:
            rows = [
                {
                    "source_name": raw_name,
                    "pueblo_magico": _canonical_name(raw_name.title(), "pueblo_magico", aliases),
                    "source_snapshot": str(PUEBLOS_MANUAL_HTML.relative_to(ROOT)),
                    "requested_snapshot": str(PUEBLOS_HTML.relative_to(ROOT)),
                    "extraction_note": "manual_browser_snapshot_iframe_titles",
                }
                for raw_name in names
            ]
            return (
                pd.DataFrame(rows)
                .drop_duplicates("pueblo_magico")
                .sort_values("pueblo_magico", kind="stable")
                .reset_index(drop=True)
            )

    # Fallback: if the direct snapshot is a CAPTCHA or the manual capture is
    # absent/invalid, use the Pueblos Mágicos menu embedded in the frozen
    # official Veracruz Turismo products page. This remains local/reproducible.
    pueblo_html = _text(PUEBLOS_HTML)
    challenged = "Radware Captcha Page" in pueblo_html or "captcha" in pueblo_html.lower()
    source = PRODUCTS_HTML if challenged else PUEBLOS_HTML
    soup = BeautifulSoup(_text(source), "html.parser")

    anchor = None
    for a in soup.find_all("a"):
        if re.sub(r"\s+", " ", a.get_text(" ", strip=True)).strip() == "Pueblos Mágicos":
            if a.find_next_sibling("ul") is not None:
                anchor = a
                break
    if anchor is None:
        raise AssertionError("Could not locate Pueblos Mágicos list in frozen source")

    rows = []
    for child in anchor.find_next_sibling("ul").find_all("a"):
        raw_name = re.sub(r"\s+", " ", child.get_text(" ", strip=True)).strip()
        if not raw_name or raw_name == "Rutas mágicas de Veracruz":
            continue
        rows.append(
            {
                "source_name": raw_name,
                "pueblo_magico": _canonical_name(raw_name, "pueblo_magico", aliases),
                "source_snapshot": str(source.relative_to(ROOT)),
                "requested_snapshot": str(PUEBLOS_HTML.relative_to(ROOT)),
                "extraction_note": (
                    "fallback_to_products_snapshot_due_to_captcha"
                    if challenged
                    else "direct_pueblos_snapshot"
                ),
            }
        )
    out = pd.DataFrame(rows).drop_duplicates("pueblo_magico")
    if len(out) != 8:
        raise AssertionError(f"Expected 8 Pueblos Mágicos, got {len(out)}")
    return out.sort_values("pueblo_magico", kind="stable").reset_index(drop=True)


def main() -> None:
    OUTDIR.mkdir(parents=True, exist_ok=True)
    products = parse_products()
    regions = parse_regions()
    pueblos = parse_pueblos_magicos()
    products.to_csv(PRODUCTS_OUT, index=False)
    regions.to_csv(REGIONS_OUT, index=False)
    pueblos.to_csv(PUEBLOS_OUT, index=False)
    print(f"Wrote {len(products):,} rows -> {PRODUCTS_OUT.relative_to(ROOT)}")
    print(f"Wrote {len(regions):,} rows -> {REGIONS_OUT.relative_to(ROOT)}")
    print(f"Wrote {len(pueblos):,} rows -> {PUEBLOS_OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
