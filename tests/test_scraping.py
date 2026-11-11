import pytest

from tablets_devops.scraping import extraer_ficha, limpiar, numero_precio


@pytest.mark.parametrize("value", [None, "no disponible", "0", 0, -1, "NaN", "Infinity"])
def test_reject_invalid_prices(value):
    assert numero_precio(value) is None


@pytest.mark.parametrize("value,expected", [(699030, 699030.0), ("12.50", 12.5)])
def test_numeric_prices(value, expected):
    assert numero_precio(value) == expected


def test_whitespace():
    assert limpiar(" Tablet   Redmi\n Pad ") == "Tablet Redmi Pad"
    assert limpiar(None) is None


def test_real_focal_product(focal_html):
    row, fragment = extraer_ficha(focal_html, "https://www.alkosto.com/tablet/p/6932554444525", "2026-10-27T20:18:14-05:00")
    assert row["SKU"] == "6932554444525"
    assert row["Precio_COP"] == 699030.0
    assert row["Marca"] == "XIAOMI"
    assert extraer_ficha(fragment, row["URL"], row["Fecha_captura"])[0] == row


def test_missing_offer_rejected():
    with pytest.raises(ValueError, match="oferta"):
        extraer_ficha(b"<html><h1>Tablet</h1></html>", "https://www.alkosto.com/p/1", "2026-10-27T20:18:14-05:00")


def test_wrong_currency_rejected(focal_html):
    with pytest.raises(ValueError, match="COP"):
        extraer_ficha(focal_html.replace(b'content="COP"', b'content="USD"'), "https://www.alkosto.com/p/1", "2026-10-27T20:18:14-05:00")
