import json

from tablets_devops.cli import main


def test_build_command(tmp_path, capsys):
    assert main(["build", "--output", str(tmp_path / "site"), "--commit", "prueba-local"]) == 0
    assert json.loads(capsys.readouterr().out)["result"]["records"] == 80


def test_replay_command(tmp_path, capsys):
    csv = tmp_path / "catalogo.csv"
    assert main(["replay", "--output", str(csv)]) == 0
    assert csv.is_file()
    assert json.loads(capsys.readouterr().out)["result"]["records"] == 80
