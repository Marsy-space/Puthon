import pytest

from lab.errors import DuplicateStudentError, StudentNotFoundError
from lab.models import Student
from lab.processing import (
    add_student,
    filter_by_min_average,
    filter_by_name_substring,
    group_stats,
    remove_student,
    sort_students,
    top_n,
    update_grades,
)


def test_add_student(sample_students):
    add_student(sample_students, Student(id=6, name="Новый", grades=[]))
    assert len(sample_students) == 6


def test_add_duplicate_raises(sample_students):
    with pytest.raises(DuplicateStudentError):
        add_student(sample_students, Student(id=1, name="Дубль", grades=[]))


def test_remove_student(sample_students):
    remove_student(sample_students, 1)
    assert len(sample_students) == 4
    assert all(s.id != 1 for s in sample_students)


def test_remove_missing_raises(sample_students):
    with pytest.raises(StudentNotFoundError):
        remove_student(sample_students, 999)


def test_update_grades(sample_students):
    update_grades(sample_students, 2, [100, 100])
    updated = next(s for s in sample_students if s.id == 2)
    assert updated.grades == [100, 100]


def test_update_grades_missing_raises(sample_students):
    with pytest.raises(StudentNotFoundError):
        update_grades(sample_students, 999, [50])


def test_sort_by_avg_descending(sample_students):
    ordered = sort_students(sample_students, key="avg")
    averages = [s.average for s in ordered]
    assert averages == sorted(averages, reverse=True)


def test_sort_by_name(sample_students):
    ordered = sort_students(sample_students, key="name")
    names = [s.name.lower() for s in ordered]
    assert names == sorted(names)


def test_sort_by_id(sample_students):
    ordered = sort_students(sample_students, key="id")
    assert [s.id for s in ordered] == [1, 2, 3, 4, 5]


def test_sort_invalid_key_raises(sample_students):
    with pytest.raises(ValueError):
        sort_students(sample_students, key="bad")


def test_sort_does_not_mutate_original(sample_students):
    original_order = [s.id for s in sample_students]
    sort_students(sample_students, key="name")
    assert [s.id for s in sample_students] == original_order


def test_filter_by_min_average(sample_students):
    result = filter_by_min_average(sample_students, 85)
    assert all(s.average >= 85 for s in result)


def test_filter_by_name_substring(sample_students):
    result = filter_by_name_substring(sample_students, "анна")
    assert len(result) == 1
    assert result[0].id == 3


def test_group_stats(sample_students):
    stats = group_stats(sample_students)
    assert stats["count"] == 5
    assert stats["best"].id == 3
    assert stats["overall_avg"] > 0


def test_group_stats_empty_list():
    stats = group_stats([])
    assert stats["count"] == 0
    assert stats["overall_avg"] == 0.0
    assert stats["best"] is None
    assert stats["worst"] is None


def test_top_n(sample_students):
    winners = top_n(sample_students, 2)
    assert len(winners) == 2
    assert winners[0].average >= winners[1].average


def test_top_n_more_than_available(sample_students):
    winners = top_n(sample_students, 100)
    assert len(winners) == len(sample_students)
