"""Extractores de BeautifulSoup adaptados del proyecto de la Unidad 1."""

import re
from decimal import Decimal, InvalidOperation

from bs4 import BeautifulSoup


def limpiar(valor):
    return ' '.join(str(valor).split()) if valor is not None else None

def numero_precio(valor):
    try:
        valor = Decimal(str(valor))
        return float(valor) if valor.is_finite() and valor >= 0 else None
    except (InvalidOperation, ValueError):
        return None

def valor_html(raiz, selector):
    nodo = raiz.select_one(selector)
    if nodo is None:
        return None
    return limpiar(nodo.get('content') or nodo.get('href') or nodo.get_text(' ', strip=True))

def extraer_ficha(html, url, fecha):
    """Única técnica de scraping: BeautifulSoup sobre el HTML recibido."""
    soup = BeautifulSoup(html, 'lxml')
    nombre = valor_html(soup, 'h1[itemprop="name"], h1')
    sku = valor_html(soup, '[itemprop="sku"]')
    if not sku:
        coincidencia = re.search(r'/p/(\d+)', url)
        sku = coincidencia.group(1) if coincidencia else None
    ofertas = soup.select_one('[itemprop="offers"]')
    if ofertas is None:
        raise ValueError('La ficha no contiene microdatos de oferta en el HTML.')
    marca = valor_html(soup, '[itemprop="brand"] [itemprop="name"]')
    precio = numero_precio(valor_html(ofertas, '[itemprop="price"]'))
    moneda = valor_html(ofertas, '[itemprop="priceCurrency"]')
    vendedor = valor_html(ofertas, '[itemprop="seller"] [itemprop="name"]')
    disponibilidad = valor_html(ofertas, '[itemprop="availability"]')
    condicion = valor_html(ofertas, '[itemprop="itemCondition"]')
    if not all([sku, nombre, marca, precio, moneda, vendedor, disponibilidad, condicion]):
        raise ValueError('La ficha tiene campos obligatorios incompletos.')
    if moneda != 'COP':
        raise ValueError('El precio no está expresado en COP.')
    if not re.search(r'\btablet|\bipad', nombre, re.I):
        raise ValueError('El nombre no identifica una tablet o iPad.')
    pantalla = re.search(r'\b\d+(?:[.,]\d+)?\s*(?:pulgadas|\")', nombre, re.I)
    capacidades = list(re.finditer(r'\b(\d+)\s*(GB|TB)\b', nombre, re.I))
    capacidad = next((x.group(0) for x in capacidades if int(x.group(1)) >= 32 or x.group(2).upper() == 'TB'), None)
    ram = re.search(r'\b\d+\s*GB\s*(?:de\s*)?RAM\b', nombre, re.I)
    fila = {
        'SKU': str(sku),
        'Nombre': nombre,
        'Marca': marca,
        'Precio_COP': precio,
        'Moneda': moneda,
        'Vendedor': vendedor,
        'Disponibilidad': disponibilidad.rsplit('/', 1)[-1],
        'Condicion_publicada': condicion.rsplit('/', 1)[-1],
        'Pantalla_en_titulo': pantalla.group(0) if pantalla else None,
        'Capacidad_en_titulo': capacidad,
        'RAM_en_titulo': ram.group(0) if ram else None,
        'Reacondicionado_en_titulo': bool(re.search(r'reacondicionad', nombre, re.I)),
        'URL': url,
        'Fecha_captura': fecha,
        'Fuente_extraccion': 'Microdatos HTML con BeautifulSoup',
    }
    # Conserva los elementos originales necesarios para repetir la extracción.
    partes = [str(soup.select_one('h1[itemprop="name"], h1'))]
    for selector in ['[itemprop="sku"]', '[itemprop="brand"]', '[itemprop="offers"]']:
        nodo = soup.select_one(selector)
        if nodo is not None:
            partes.append(str(nodo))
    fragmento = ('<!doctype html><html><head><meta charset="utf-8"></head><body>\n' + '\n'.join(partes) + '\n</body></html>').encode('utf-8')
    return fila, fragmento
