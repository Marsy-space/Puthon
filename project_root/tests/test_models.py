import pytest

from lab.errors import ValidationError
from lab.models import Student, validate_grade, validate_id, validate_name


def test_average_with_grades():
    s = Student(id=1, name="Тест", grades=[80, 90, 100])
    assert s.average == pytest.approx(90.0)


def test_average_empty_list_is_zero():
    s = Student(id=1, name="Тест", grades=[])
    assert s.average == 0.0


def test_average_ignores_none():
    s = Student(id=1, name="Тест", grades=[80, None, 100])
    assert s.average == pytest.approx(90.0)


def test_average_all_none_is_zero():
    s = Student(id=1, name="Тест", grades=[None, None])
    assert s.average == 0.0


@pytest.mark.parametrize("raw,expected", [("5", 5), (" 5 ", 5), (5, 5)])
def test_validate_id_valid(raw, expected):
    assert validate_id(raw) == expected


@pytest.mark.parametrize("raw", ["abc", "-1", "1.5", None])
def test_validate_id_invalid(raw):
    with pytest.raises(ValidationError):
        validate_id(raw)


def test_validate_name_valid():
    assert validate_name("  Иванов Иван  ") == "Иванов Иван"


def test_validate_name_empty_raises():
    with pytest.raises(ValidationError):
        validate_name("   ")


@pytest.mark.parametrize("raw,expected", [("", None), (None, None), ("0", 0), ("100", 100), (50, 50)])
def test_validate_grade_valid(raw, expected):
    assert validate_grade(raw) == expected


@pytest.mark.parametrize("raw", ["-1", "101", "abc", "5.5"])
def test_validate_grade_invalid(raw):
    with pytest.raises(ValidationError):
        validate_grade(raw)
