"""Publicación estática del análisis, con datos y versión comprobables."""

import json
from datetime import datetime, timezone
from html import escape
from pathlib import Path

import pandas as pd

from tablets_devops.analysis import summarize
from tablets_devops.data import save_csv, validate_dataset


def cop(value: float) -> str:
    return "$" + f"{value:,.0f}".replace(",", ".")


def build_site(frame: pd.DataFrame, output: Path, commit: str = "local", run_url: str = "") -> dict:
    """Genera una publicación sin llamadas al comercio durante CI."""
    quality = validate_dataset(frame, minimum_rows=50)
    summary = summarize(frame)
    output.mkdir(parents=True, exist_ok=True)
    health = {"status": "ok", "version": "2.0.0", "commit": commit, "run_url": run_url,
              "records": len(frame), "generated_utc": datetime.now(timezone.utc).isoformat(),
              "capture_start": summary["capture_start"], "capture_end": summary["capture_end"],
              "quality": quality}
    for filename, data in [("health.json", health), ("summary.json", summary)]:
        (output / filename).write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    save_csv(frame, output / "catalogo_tablets.csv")
    rows = []
    for _, row in frame.iterrows():
        stock = "Disponible" if row["Disponibilidad"] == "InStock" else "Sin existencias"
        rows.append(
            f'<tr data-brand="{escape(str(row["Marca"]))}" data-stock="{escape(str(row["Disponibilidad"]))}" '
            f'data-price="{row["Precio_COP"]}"><td><a href="{escape(str(row["URL"]))}" target="_blank" rel="noopener noreferrer">'
            f'{escape(str(row["Nombre"]))}</a><small>SKU {escape(str(row["SKU"]))}</small></td>'
            f'<td>{escape(str(row["Marca"]))}</td><td class="money">{cop(row["Precio_COP"])}</td>'
            f'<td><span class="stock {"available" if stock == "Disponible" else "empty"}">{stock}</span></td></tr>'
        )
    options = "".join(f'<option>{escape(str(brand))}</option>' for brand in sorted(frame["Marca"].unique()))
    bars = "".join(
        f'<div class="bar-row"><span>{escape(item["brand"])}</span><div class="track"><div style="width:{item["count"]/len(frame)*100:.2f}%"></div></div><b>{item["count"]}</b></div>'
        for item in summary["by_brand"]
    )
    html = f'''<!doctype html>
<html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Catálogo de tablets · Unidad 2</title><link rel="stylesheet" href="styles.css"><script defer src="app.js"></script></head>
<body><header><div class="wrap"><div class="eyebrow">ANÁLISIS DE DATOS · EVIDENCIA 2</div><h1>El catálogo de tablets,<br>en una sola vista.</h1>
<p>80 referencias de Alkosto para comparar precios publicados, marcas y disponibilidad.</p>
<div class="source">Captura del 27 de octubre de 2026 · Artículo central: Redmi Pad 2 de 128 GB</div></div></header>
<main class="wrap"><section class="metrics" aria-label="Resumen del catálogo">
<article><span>Referencias</span><strong>{summary["records"]}</strong><small>SKU únicos</small></article>
<article><span>Marcas declaradas</span><strong>{summary["brands"]}</strong><small>Según las fichas</small></article>
<article><span>Disponibles</span><strong>{summary["in_stock"]}</strong><small>En la captura original</small></article>
<article><span>Precio mediano</span><strong>{cop(summary["median_cop"])}</strong><small>Pesos colombianos</small></article></section>
<section class="panel"><div class="section-heading"><div><h2>Explorar las referencias</h2><p>Filtra la tabla o descarga los datos completos.</p></div>
<a class="button" href="catalogo_tablets.csv" download>Descargar CSV</a></div>
<div class="filters"><label>Buscar<input id="search" type="search" placeholder="Nombre o SKU"></label>
<label>Marca<select id="brand"><option value="">Todas las marcas</option>{options}</select></label>
<label>Disponibilidad<select id="stock"><option value="">Todos los estados</option><option value="InStock">Disponible</option><option value="OutOfStock">Sin existencias</option></select></label>
<button id="sort" type="button">Precio: menor primero</button></div><p id="count" class="count">{len(frame)} referencias</p>
<div class="table-scroll"><table><thead><tr><th>Artículo</th><th>Marca</th><th>Precio COP</th><th>Disponibilidad</th></tr></thead><tbody>{"".join(rows)}</tbody></table></div></section>
<section class="panel comparison"><div><h2>Referencias por marca declarada</h2><p>Las variantes de color y capacidad pueden tener SKU distintos.</p>{bars}</div>
<aside><h2>Cómo leer estos datos</h2><p>Los precios y estados corresponden a la fecha de captura. La publicación no realiza una nueva consulta al comercio.</p>
<p>En algunas fichas reacondicionadas aparece Alkosto como marca. La condición publicada y la descripción del título se conservan por separado en el CSV.</p>
<p>Este conjunto permite comparar publicaciones; no contiene unidades vendidas.</p></aside></section>
</main><footer class="wrap">Marlon Monterrosa · Unidad 2 · BeautifulSoup · Versión {escape(commit[:12])}<br>
<a href="health.json">Estado de la publicación</a> · <a href="summary.json">Resumen de los datos</a></footer></body></html>'''
    (output / "index.html").write_text(html, encoding="utf-8")
    (output / "styles.css").write_text(STYLES, encoding="utf-8")
    (output / "app.js").write_text(APP_JS, encoding="utf-8")
    (output / ".nojekyll").write_text("", encoding="utf-8")
    return health


STYLES = """
*{box-sizing:border-box}body{margin:0;background:#f4f7fb;color:#14253b;font:15px/1.55 system-ui,sans-serif}.wrap{max-width:1160px;margin:auto;padding:0 28px}
header{padding:48px 0 72px;background:#102f52;color:white}.eyebrow{font-size:11px;letter-spacing:.16em;color:#8cd6cf;font-weight:700}h1{font-size:44px;line-height:1.13;letter-spacing:-.04em;margin:18px 0}header p{color:#d4e2ed}.source{font-size:12px;color:#b8d0e3}
.metrics{display:grid;grid-template-columns:repeat(4,1fr);gap:16px;margin-top:-35px;margin-bottom:30px}.metrics article{background:white;border:1px solid #e2e8ef;border-radius:12px;padding:23px;box-shadow:0 5px 18px #12345608}.metrics span,.metrics small{display:block;color:#607389}.metrics strong{font-size:30px;display:block;margin:6px 0;letter-spacing:-.04em}.metrics small{font-size:11px}
.panel{background:white;border:1px solid #e2e8ef;border-radius:13px;padding:26px;margin:24px 0}h2{font-size:20px;letter-spacing:-.02em;margin:0 0 6px}p{margin:6px 0 18px}.section-heading{display:flex;align-items:center;justify-content:space-between;gap:20px}.section-heading p,.comparison p{color:#607389}.button,button{background:#136b68;color:white;border:0;border-radius:7px;padding:10px 15px;font:inherit;font-size:13px;text-decoration:none;cursor:pointer;white-space:nowrap}
.filters{display:grid;grid-template-columns:2fr 1fr 1fr auto;gap:12px;align-items:end;margin-top:20px}label{display:block;font-size:12px;font-weight:600}input,select{width:100%;background:#fff;border:1px solid #cfd9e3;border-radius:7px;padding:10px;margin-top:6px;color:#20384e;font:inherit;font-size:13px}.count{font-size:12px;color:#61768c;margin:15px 0 8px}.table-scroll{max-height:560px;overflow:auto}table{width:100%;border-collapse:collapse;text-align:left;font-size:13px}th{position:sticky;top:0;background:#eef3f7;font-size:11px;color:#53677b;z-index:1}td,th{padding:13px 12px;border-bottom:1px solid #e8edf2}td:first-child{min-width:300px;max-width:490px}td a{color:#183e5f;text-decoration:none}td a:hover{text-decoration:underline}small{display:block;color:#74879a;font-size:10px}.money{white-space:nowrap;font-variant-numeric:tabular-nums;font-weight:650}.stock{font-size:10px;white-space:nowrap;padding:4px 8px;border-radius:30px}.available{background:#e3f3ed;color:#1c7057}.empty{background:#f0f2f5;color:#718093}.comparison{display:grid;grid-template-columns:1.15fr 1fr;gap:50px}.bar-row{display:grid;grid-template-columns:85px 1fr 25px;gap:10px;align-items:center;font-size:11px;margin:12px 0}.track{background:#f0f4f7;border-radius:8px;height:8px;overflow:hidden}.track div{height:100%;background:#27827e;border-radius:8px}aside{border-left:1px solid #e2e8ef;padding-left:30px}footer{font-size:11px;color:#718093;padding-top:12px!important;padding-bottom:32px!important}footer a{color:#416784}
@media(max-width:800px){h1{font-size:34px}.metrics{grid-template-columns:repeat(2,1fr)}.filters{grid-template-columns:1fr 1fr}.comparison{grid-template-columns:1fr;gap:20px}aside{border-left:0;border-top:1px solid #e2e8ef;padding-left:0;padding-top:24px}.section-heading{align-items:start}.metrics strong{font-size:25px}}@media(max-width:450px){.wrap{padding:0 16px}.panel{padding:18px}.section-heading{display:block}.metrics{gap:10px}.metrics article{padding:16px}h1{font-size:30px}.filters{grid-template-columns:1fr}.button{display:inline-block}}
"""

APP_JS = """
const rows = [...document.querySelectorAll('tbody tr')];
const search = document.querySelector('#search');
const brand = document.querySelector('#brand');
const stock = document.querySelector('#stock');
function filterRows(){let count=0;for(const row of rows){const show=row.textContent.toLocaleLowerCase('es').includes(search.value.toLocaleLowerCase('es'))&&(!brand.value||row.dataset.brand===brand.value)&&(!stock.value||row.dataset.stock===stock.value);row.hidden=!show;if(show)count++;}document.querySelector('#count').textContent=count+' referencias';}
for(const el of [search,brand,stock]){el.addEventListener('input',filterRows);}
document.querySelector('#sort').addEventListener('click',()=>{const body=document.querySelector('tbody');for(const row of [...rows].sort((a,b)=>Number(a.dataset.price)-Number(b.dataset.price))){body.appendChild(row);}});
"""
