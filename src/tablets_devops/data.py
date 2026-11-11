"""Reproducción verificable y validación de los datos de la Unidad 1."""

import hashlib
import json
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse

import pandas as pd

from tablets_devops.scraping import extraer_ficha

ESSENTIAL = [
    "SKU", "Nombre", "Marca", "Precio_COP", "Moneda", "Vendedor", "Disponibilidad",
    "Condicion_publicada", "URL", "Fecha_captura", "Fuente_extraccion",
]


def validate_dataset(frame: pd.DataFrame, minimum_rows: int = 1) -> dict:
    """Rechaza datos incompletos, duplicados o precios que no puedan compararse."""
    missing = sorted(set(ESSENTIAL) - set(frame.columns))
    if missing:
        raise ValueError(f"Faltan columnas esenciales: {missing}")
    if len(frame) < minimum_rows:
        raise ValueError(f"Se requieren al menos {minimum_rows} referencias.")
    presence = frame[ESSENTIAL].notna() & frame[ESSENTIAL].astype(str).apply(lambda c: c.str.strip().ne(""))
    if not presence.all().all():
        raise ValueError("Hay campos esenciales vacíos.")
    if frame["SKU"].astype(str).duplicated().any():
        raise ValueError("Hay SKU duplicados.")
    prices = pd.to_numeric(frame["Precio_COP"], errors="coerce")
    if prices.isna().any() or not prices.gt(0).all() or prices.isin([float("inf"), -float("inf")]).any():
        raise ValueError("Hay precios inválidos.")
    if not frame["Moneda"].eq("COP").all():
        raise ValueError("Todos los precios deben estar expresados en COP.")
    for url in frame["URL"]:
        parsed = urlparse(str(url))
        if parsed.scheme != "https" or parsed.hostname != "www.alkosto.com":
            raise ValueError("La URL de origen no corresponde a Alkosto por HTTPS.")
    for value in frame["Fecha_captura"]:
        date = datetime.fromisoformat(str(value))
        if date.tzinfo is None:
            raise ValueError("La fecha de captura debe incluir zona horaria.")
    return {"records": len(frame), "essential_fields": len(ESSENTIAL), "completeness_pct": 100.0,
            "duplicates": 0, "valid_prices_pct": 100.0}


def replay_snapshot(snapshot: Path) -> tuple[pd.DataFrame, dict]:
    """Vuelve a extraer las fichas y verifica la integridad de cada fragmento."""
    snapshot = Path(snapshot).resolve()
    manifest = json.loads((snapshot / "captura_catalogo.json").read_text(encoding="utf-8"))
    records = manifest.get("registros", [])
    if not records:
        raise ValueError("La captura no contiene fichas.")
    rows = []
    for record in records:
        path = (snapshot / record["fragmento"]).resolve()
        if not path.is_relative_to(snapshot):
            raise ValueError("El fragmento está fuera de la carpeta de evidencia.")
        html = path.read_bytes()
        if hashlib.sha256(html).hexdigest() != record["sha256_fragmento"]:
            raise ValueError(f"El fragmento fue modificado: {record['sku']}")
        row, _ = extraer_ficha(html, record["url"], record["fecha"])
        rows.append(row)
    frame = pd.DataFrame(rows)
    validate_dataset(frame)
    return frame, manifest


def save_csv(frame: pd.DataFrame, path: Path) -> None:
    """Exporta el mismo formato de CSV usado en la Unidad 1."""
    path.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(path, index=False, sep=";", encoding="utf-8-sig", decimal=",")
