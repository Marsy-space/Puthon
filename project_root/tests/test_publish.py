import json

import pytest

from lab.errors import FileAccessError
from lab.publish import build_snapshot, publish


def test_snapshot_contains_students_and_stats(sample_students):
    snap = build_snapshot(sample_students)
    assert len(snap["students"]) == 5
    assert snap["stats"]["count"] == 5
    assert snap["stats"]["best"]["id"] == 4
    assert "version" in snap and "generated_at" in snap


def test_version_depends_only_on_data(sample_students):
    assert build_snapshot(sample_students)["version"] == build_snapshot(sample_students)["version"]
    sample_students[0].grades = [1, 2]
    assert build_snapshot(sample_students)["version"] != build_snapshot(
        [s for s in sample_students[1:]]
    )["version"]


def test_publish_writes_then_skips_when_unchanged(tmp_path):
    csv_path = tmp_path / "s.csv"
    out = tmp_path / "site" / "data.json"
    csv_path.write_text("id,name,grade1\n1,Иванов Иван,80\n", encoding="utf-8")

    assert publish(str(csv_path), str(out)) is True
    assert json.loads(out.read_text(encoding="utf-8"))["stats"]["count"] == 1
    assert publish(str(csv_path), str(out)) is False  


def test_publish_updates_when_csv_changes(tmp_path):
    csv_path = tmp_path / "s.csv"
    out = tmp_path / "data.json"
    csv_path.write_text("id,name,grade1\n1,Иванов Иван,80\n", encoding="utf-8")
    publish(str(csv_path), str(out))
    csv_path.write_text("id,name,grade1\n1,Иванов Иван,80\n2,Петров Петр,60\n", encoding="utf-8")
    assert publish(str(csv_path), str(out)) is True
    assert json.loads(out.read_text(encoding="utf-8"))["stats"]["count"] == 2


def test_publish_missing_csv_raises(tmp_path):
    with pytest.raises(FileAccessError):
        publish(str(tmp_path / "nope.csv"), str(tmp_path / "data.json"))
