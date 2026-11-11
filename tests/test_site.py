import json

from bs4 import BeautifulSoup

from tablets_devops.site import build_site, cop


def test_site_has_valid_data_and_version(dataset, tmp_path):
    health = build_site(dataset, tmp_path, "a" * 40, "https://github.com/example/actions/runs/1")
    assert health["commit"] == "a" * 40
    assert health["records"] == 80
    assert json.loads((tmp_path / "health.json").read_text())["status"] == "ok"
    soup = BeautifulSoup((tmp_path / "index.html").read_text(encoding="utf-8"), "html.parser")
    assert len(soup.select("tbody tr")) == 80
    assert len(soup.select(".available")) == 44
    assert (tmp_path / "catalogo_tablets.csv").is_file()
    assert (tmp_path / "app.js").is_file()
    assert (tmp_path / "styles.css").is_file()
    assert (tmp_path / ".nojekyll").is_file()
    assert cop(699030) == "$699.030"


def test_external_titles_are_escaped(dataset, tmp_path):
    frame = dataset.copy()
    frame.loc[0, "Nombre"] = '<script>alert("prueba")</script>'
    build_site(frame, tmp_path)
    soup = BeautifulSoup((tmp_path / "index.html").read_text(encoding="utf-8"), "html.parser")
    assert len(soup.find_all("script")) == 1  # Solo el script propio de la aplicación.
    assert soup.select_one("tbody tr td a").get_text() == '<script>alert("prueba")</script>'
