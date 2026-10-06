from pathlib import Path
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"

REQUIRED_FILES = {
    "Base70centros.csv": 2_000_000,
    "INAH_visitantes_zonas_general.csv": 500_000,
    "INAH_zonas_arqueologicas.csv": 30_000,
    "PIB_Turistico_Estatal_y_Municipal_2018-2022_.zip": 5_000_000,
    "denue_00_48-49_csv.zip": 4_000_000,
    "denue_00_56_shp.zip": 10_000_000,
    "denue_00_71_csv.zip": 5_000_000,
    "denue_00_72_1_csv.zip": 40_000_000,
    "denue_00_72_2_csv.zip": 20_000_000,
    "veracruz_productos_2026-10-06.html": 1_000,
    "veracruz_regiones_2026-10-06.html": 1_000,
    "veracruz_pueblos_magicos_2026-10-06.html": 1_000,
}


def test_required_raw_sources_exist_and_are_nontrivial():
    missing = [name for name in REQUIRED_FILES if not (RAW / name).is_file()]
    assert not missing, f"Missing raw sources: {missing}"
    too_small = {
        name: (RAW / name).stat().st_size
        for name, minimum in REQUIRED_FILES.items()
        if (RAW / name).stat().st_size < minimum
    }
    assert not too_small, f"Raw files unexpectedly small (failed/partial download?): {too_small}"


def test_denue_archives_are_2026_snapshot_and_contain_data():
    for name in [
        "denue_00_48-49_csv.zip",
        "denue_00_56_shp.zip",
        "denue_00_71_csv.zip",
        "denue_00_72_1_csv.zip",
        "denue_00_72_2_csv.zip",
    ]:
        with ZipFile(RAW / name) as zf:
            metadata = [n for n in zf.namelist() if n.endswith("metadatos_denue.txt")]
            assert metadata, f"No DENUE metadata in {name}"
            text = zf.read(metadata[0]).decode("utf-8-sig", errors="replace")
            assert "DENUE-2026" in text or "05_2026" in text
            assert any("conjunto_de_datos/" in n for n in zf.namelist())


def test_sector_71_is_corrected_2026_release():
    with ZipFile(RAW / "denue_00_71_csv.zip") as zf:
        metadata = [n for n in zf.namelist() if n.endswith("metadatos_denue.txt")][0]
        text = zf.read(metadata).decode("utf-8-sig", errors="replace")
        assert "2026" in text
        assert "1 de julio de 2026" in text or "julio de 2026" in text
