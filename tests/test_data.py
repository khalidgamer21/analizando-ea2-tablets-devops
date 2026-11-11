import json
import shutil

import pandas as pd
import pytest

from tablets_devops.data import replay_snapshot, save_csv, validate_dataset

from .conftest import ROOT


def test_snapshot_matches_ea1_csv(dataset):
    expected = pd.read_csv(ROOT / "data" / "catalogo_tablets.csv", sep=";", decimal=",", dtype={"SKU": str})
    pd.testing.assert_frame_equal(dataset, expected, check_dtype=False)
    assert dataset.shape == (80, 15)
    assert validate_dataset(dataset, minimum_rows=50)["completeness_pct"] == 100.0


@pytest.mark.parametrize("kind", ["empty", "column", "null", "duplicate", "negative", "infinite", "currency", "url", "date"])
def test_invalid_data_is_blocked(dataset, kind):
    frame = dataset.head(2).copy()
    if kind == "empty":
        frame = frame.iloc[:0]
    elif kind == "column":
        frame = frame.drop(columns="Marca")
    elif kind == "null":
        frame.loc[0, "Nombre"] = None
    elif kind == "duplicate":
        frame.loc[1, "SKU"] = frame.loc[0, "SKU"]
    elif kind == "negative":
        frame.loc[0, "Precio_COP"] = -1.0
    elif kind == "infinite":
        frame.loc[0, "Precio_COP"] = float("inf")
    elif kind == "currency":
        frame.loc[0, "Moneda"] = "USD"
    elif kind == "url":
        frame.loc[0, "URL"] = "http://example.com/producto"
    elif kind == "date":
        frame.loc[0, "Fecha_captura"] = "2026-10-27T20:18:14"
    with pytest.raises(ValueError):
        validate_dataset(frame)


def test_export_roundtrip(dataset, tmp_path):
    destination = tmp_path / "nested" / "catalogo.csv"
    save_csv(dataset, destination)
    restored = pd.read_csv(destination, sep=";", decimal=",", dtype={"SKU": str})
    pd.testing.assert_frame_equal(restored, dataset, check_dtype=False)


@pytest.mark.parametrize("kind", ["tampered", "escape", "empty"])
def test_integrity_checks(tmp_path, kind):
    snapshot = tmp_path / "snapshot"
    shutil.copytree(ROOT / "data" / "snapshot", snapshot)
    path = snapshot / "captura_catalogo.json"
    manifest = json.loads(path.read_text(encoding="utf-8"))
    if kind == "tampered":
        fragment = snapshot / manifest["registros"][0]["fragmento"]
        fragment.write_bytes(fragment.read_bytes() + b"changed")
    elif kind == "escape":
        manifest["registros"][0]["fragmento"] = "../outside.html"
    else:
        manifest["registros"] = []
    path.write_text(json.dumps(manifest), encoding="utf-8")
    with pytest.raises(ValueError):
        replay_snapshot(snapshot)
