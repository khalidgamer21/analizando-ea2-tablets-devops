"""Estadísticas descriptivas de precios; no estima unidades vendidas."""

import pandas as pd

from tablets_devops.data import validate_dataset


def summarize(frame: pd.DataFrame) -> dict:
    validate_dataset(frame)
    groups = frame.groupby("Marca")["Precio_COP"].agg(["count", "min", "median", "max"])
    groups = groups.sort_values(["count", "median"], ascending=[False, True])
    return {
        "records": len(frame),
        "brands": int(frame["Marca"].nunique()),
        "in_stock": int(frame["Disponibilidad"].eq("InStock").sum()),
        "out_of_stock": int(frame["Disponibilidad"].eq("OutOfStock").sum()),
        "minimum_cop": float(frame["Precio_COP"].min()),
        "median_cop": float(frame["Precio_COP"].median()),
        "maximum_cop": float(frame["Precio_COP"].max()),
        "refurbished_in_title": int(frame["Reacondicionado_en_titulo"].sum()),
        "capture_start": str(frame["Fecha_captura"].min()),
        "capture_end": str(frame["Fecha_captura"].max()),
        "by_brand": [{"brand": str(brand), "count": int(row["count"]),
                      "minimum_cop": float(row["min"]), "median_cop": float(row["median"]),
                      "maximum_cop": float(row["max"])} for brand, row in groups.iterrows()],
    }
