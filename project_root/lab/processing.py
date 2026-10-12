"""Функции обработки списка студентов: CRUD, сортировка, статистика, ТОП-N."""

from typing import Dict, List, Optional

from lab.errors import DuplicateStudentError, StudentNotFoundError
from lab.models import Student

VALID_SORT_KEYS = ("avg", "name", "id")


def find_student(students: List[Student], student_id: int) -> Optional[Student]:
    """Возвращает студента по id или None, если не найден."""
    for s in students:
        if s.id == student_id:
            return s
    return None


def add_student(students: List[Student], student: Student) -> None:
    """Добавляет студента в список. Бросает DuplicateStudentError,
    если студент с таким id уже есть."""
    if find_student(students, student.id) is not None:
        raise DuplicateStudentError(f"Студент с id={student.id} уже существует")
    students.append(student)


def remove_student(students: List[Student], student_id: int) -> None:
    """Удаляет студента по id. Бросает StudentNotFoundError, если не найден."""
    student = find_student(students, student_id)
    if student is None:
        raise StudentNotFoundError(f"Студент с id={student_id} не найден")
    students.remove(student)


def update_grades(students: List[Student], student_id: int, grades: List[Optional[int]]) -> None:
    """Заменяет список оценок студента по id. Бросает StudentNotFoundError,
    если студент не найден."""
    student = find_student(students, student_id)
    if student is None:
        raise StudentNotFoundError(f"Студент с id={student_id} не найден")
    student.grades = list(grades)


def sort_students(students: List[Student], key: str = "avg") -> List[Student]:
    """Возвращает НОВЫЙ отсортированный список (исходный не меняется).

    key:
      'avg'  - по убыванию среднего балла, при равенстве - по имени (a..z), для стабильности
      'name' - по имени (a..z)
      'id'   - по возрастанию id
    """
    if key not in VALID_SORT_KEYS:
        raise ValueError(f"Неизвестный ключ сортировки: {key!r}. Допустимо: {VALID_SORT_KEYS}")

    if key == "avg":
        return sorted(students, key=lambda s: (-s.average, s.name.lower()))
    if key == "name":
        return sorted(students, key=lambda s: s.name.lower())
    return sorted(students, key=lambda s: s.id)


def filter_by_min_average(students: List[Student], min_average: float) -> List[Student]:
    """Оставляет только студентов со средним баллом >= min_average."""
    return [s for s in students if s.average >= min_average]


def filter_by_name_substring(students: List[Student], substring: str) -> List[Student]:
    """Оставляет только студентов, чьё имя содержит подстроку (без учёта регистра)."""
    needle = substring.strip().lower()
    return [s for s in students if needle in s.name.lower()]


def group_stats(students: List[Student]) -> Dict[str, object]:
    """Групповая статистика: количество студентов, общий средний балл
    по всем оценкам, лучший и худший студент по среднему баллу.

    Пустой список студентов обрабатывается корректно (без деления на 0).
    """
    count = len(students)
    all_grades = [g for s in students for g in s.grades if g is not None]
    overall_avg = sum(all_grades) / len(all_grades) if all_grades else 0.0

    best = worst = None
    if students:
        best = max(students, key=lambda s: s.average)
        worst = min(students, key=lambda s: s.average)

    return {
        "count": count,
        "overall_avg": overall_avg,
        "best": best,
        "worst": worst,
    }


def top_n(students: List[Student], n: int) -> List[Student]:
    """Возвращает первых n студентов по убыванию среднего балла
    (та же логика сортировки, что и sort_students(key='avg'))."""
    if n < 0:
        raise ValueError("n не может быть отрицательным")
    return sort_students(students, key="avg")[:n]
