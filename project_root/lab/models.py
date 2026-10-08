"""Модель данных Student и функции валидации отдельных полей."""

from dataclasses import dataclass, field
from typing import List, Optional

from lab.errors import ValidationError

MIN_GRADE = 0
MAX_GRADE = 100


@dataclass
class Student:
    """Студент: id, ФИО и список оценок.
    """

    id: int
    name: str
    grades: List[Optional[int]] = field(default_factory=list)

    @property
    def average(self) -> float:
        """Средний балл по имеющимся (не пустым) оценкам.

        Если оценок нет вообще (пустой список или все пустые) -> 0.0.
        """
        valid = [g for g in self.grades if g is not None]
        return sum(valid) / len(valid) if valid else 0.0

    def grades_display(self) -> str:
        """Оценки одной строкой через пробел, пустая ставится как '-' """
        return " ".join("-" if g is None else str(g) for g in self.grades)


def validate_id(raw: object) -> int:
    """Проверяет и приводит id к int. Бросает ValidationError при ошибке."""
    try:
        value = int(str(raw).strip())
    except (ValueError, TypeError) as exc:
        raise ValidationError(f"id должен быть целым числом, получено: {raw!r}") from exc
    if value < 0:
        raise ValidationError(f"id не может быть отрицательным: {value}")
    return value


def validate_name(raw: object) -> str:
    """Проверяет ФИО: непустая строка после обрезки пробелов."""
    name = str(raw).strip()
    if not name:
        raise ValidationError("ФИО не может быть пустым")
    return name


def validate_grade(raw: object) -> Optional[int]:
    """Проверяет одну оценку.

    Пустая строка/None -> отсутствующая оценка (None).
    Иначе -> целое число в диапазоне [MIN_GRADE, MAX_GRADE].
    """
    if raw is None:
        return None
    text = str(raw).strip()
    if text == "":
        return None
    try:
        value = int(text)
    except ValueError as exc:
        raise ValidationError(f"Оценка должна быть целым числом, получено: {raw!r}") from exc
    if not (MIN_GRADE <= value <= MAX_GRADE):
        raise ValidationError(
            f"Оценка должна быть в диапазоне {MIN_GRADE}..{MAX_GRADE}, получено: {value}"
        )
    return value


def validate_grades(raw_list: List[object]) -> List[Optional[int]]:
    """Валидирует список сырых значений оценок."""
    return [validate_grade(item) for item in raw_list]
