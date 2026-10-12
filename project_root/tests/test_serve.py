import json

from lab.serve import Hub, Watcher


def make(tmp_path, text):
    csv_path = tmp_path / "s.csv"
    csv_path.write_text(text, encoding="utf-8")
    out = tmp_path / "site" / "data.json"
    return csv_path, out, Watcher(str(csv_path), str(out), Hub())


def test_first_check_publishes(tmp_path):
    csv_path, out, w = make(tmp_path, "id,name,grade1\n1,Иванов Иван,80\n")
    assert w.check() is True
    assert json.loads(out.read_text(encoding="utf-8"))["stats"]["count"] == 1


def test_no_change_no_update(tmp_path):
    csv_path, out, w = make(tmp_path, "id,name,grade1\n1,Иванов Иван,80\n")
    w.check()
    assert w.check() is False


def test_listener_sees_console_changes(tmp_path):
    csv_path, out, w = make(tmp_path, "id,name,grade1\n1,Иванов Иван,80\n")
    w.check()
    before = w.hub.counter
    csv_path.write_text("id,name,grade1\n1,Иванов Иван,80\n2,Петров Петр,60\n", encoding="utf-8")
    assert w.check() is True
    assert json.loads(out.read_text(encoding="utf-8"))["stats"]["count"] == 2
    assert w.hub.counter == before + 1  


def test_broken_file_keeps_old_data(tmp_path):
    csv_path, out, w = make(tmp_path, "id,name,grade1\n1,Иванов Иван,80\n")
    w.check()
    csv_path.write_text("id,name,grade1\n1,Иванов Иван,abc\n", encoding="utf-8")
    assert w.check() is False
    assert json.loads(out.read_text(encoding="utf-8"))["stats"]["count"] == 1
