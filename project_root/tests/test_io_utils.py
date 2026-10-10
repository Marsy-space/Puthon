import pytest

from lab.errors import CsvFormatError, FileAccessError
from lab.io_utils import export_top_n_csv, read_students_csv, write_students_csv
from lab.models import Student


def test_read_csv_with_header(tmp_path):
    p = tmp_path / "students.csv"
    p.write_text(
        "id,name,grade1,grade2\n1,Иванов Иван,78,85\n2,Петров Петр,,90\n",
        encoding="utf-8",
    )
    students = read_students_csv(str(p))
    assert len(students) == 2
    assert students[0].id == 1
    assert students[0].name == "Иванов Иван"
    assert students[1].grades == [None, 90]


def test_read_csv_without_header(tmp_path):
    p = tmp_path / "students.csv"
    p.write_text("1,Иванов Иван,78,85\n2,Петров Петр,60,70\n", encoding="utf-8")
    students = read_students_csv(str(p))
    assert len(students) == 2
    assert students[0].name == "Иванов Иван"


def test_read_csv_missing_file(tmp_path):
    with pytest.raises(FileAccessError):
        read_students_csv(str(tmp_path / "missing.csv"))


def test_read_csv_bad_row_raises_format_error(tmp_path):
    p = tmp_path / "students.csv"
    p.write_text("id,name,grade1\n1,Иванов Иван,abc\n", encoding="utf-8")
    with pytest.raises(CsvFormatError):
        read_students_csv(str(p))


def test_read_csv_not_enough_columns(tmp_path):
    p = tmp_path / "students.csv"
    p.write_text("id,name\n1\n", encoding="utf-8")
    with pytest.raises(CsvFormatError):
        read_students_csv(str(p))


def test_write_then_read_roundtrip(tmp_path, sample_students):
    p = tmp_path / "out.csv"
    write_students_csv(str(p), sample_students, with_header=True)
    loaded = read_students_csv(str(p))
    assert len(loaded) == len(sample_students)
    for original, restored in zip(sample_students, loaded):
        assert original.id == restored.id
        assert original.name == restored.name
        assert original.grades == restored.grades


def test_write_pads_grade_columns(tmp_path):
    students = [
        Student(id=1, name="A", grades=[80]),
        Student(id=2, name="B", grades=[70, 90, 100]),
    ]
    p = tmp_path / "out.csv"
    write_students_csv(str(p), students, with_header=True)
    lines = p.read_text(encoding="utf-8").splitlines()
    assert lines[0] == "id,name,grade1,grade2,grade3"
    assert lines[1] == "1,A,80,,"


def test_export_top_n_csv(tmp_path, sample_students):
    p = tmp_path / "top.csv"
    export_top_n_csv(str(p), sample_students[:2])
    lines = p.read_text(encoding="utf-8").splitlines()
    assert lines[0] == "id,name,average,grades"
    assert len(lines) == 3
