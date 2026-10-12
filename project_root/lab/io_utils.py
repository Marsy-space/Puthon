"""Чтение и запись списка студентов в формате CSV.
Формат: id,name,grade1,grade2,...,gradeN
"""

import csv
import os
from typing import List

from lab.errors import CsvFormatError, FileAccessError
from lab.models import Student, validate_grade, validate_id, validate_name

ENCODING = "utf-8"


def _looks_like_header(row: List[str]) -> bool:

    if not row:
        return False
    first = row[0].strip().lower()
    if first == "":
        return False
    try:
        int(first)
        return False
    except ValueError:
        return True


def read_students_csv(path: str) -> List[Student]:
   
    if not os.path.exists(path):
        raise FileAccessError(f"Файл не найден: {path}")
    if not os.access(path, os.R_OK):
        raise FileAccessError(f"Нет прав на чтение файла: {path}")

    students: List[Student] = []
    try:
        with open(path, "r", encoding="utf-8-sig", newline="") as f:
            reader = csv.reader(f)
            rows = [row for row in reader if any(cell.strip() for cell in row)]
    except UnicodeDecodeError as exc:
        raise CsvFormatError(f"Файл не в кодировке UTF-8: {path}") from exc
    except OSError as exc:
        raise FileAccessError(f"Ошибка чтения файла {path}: {exc}") from exc

    if not rows:
        return students

    start_index = 0
    if _looks_like_header(rows[0]):
        start_index = 1

    for line_no, row in enumerate(rows[start_index:], start=start_index + 1):
        if len(row) < 2:
            raise CsvFormatError(
                f"Строка {line_no}: недостаточно колонок (нужно минимум id,name): {row}"
            )
        try:
            sid = validate_id(row[0])
            name = validate_name(row[1])
            grades = [validate_grade(cell) for cell in row[2:]]
        except Exception as exc:
            raise CsvFormatError(f"Строка {line_no}: {exc}") from exc
        students.append(Student(id=sid, name=name, grades=grades))

    return students


def write_students_csv(path: str, students: List[Student], with_header: bool = True) -> None:
    max_grades = max((len(s.grades) for s in students), default=0)

    directory = os.path.dirname(path)
    if directory:
        os.makedirs(directory, exist_ok=True)

    try:
       
        tmp_path = path + ".tmp"
        with open(tmp_path, "w", encoding=ENCODING, newline="") as f:
            writer = csv.writer(f)
            if with_header:
                header = ["id", "name"] + [f"grade{i}" for i in range(1, max_grades + 1)]
                writer.writerow(header)
            for s in students:
                padded = list(s.grades) + [None] * (max_grades - len(s.grades))
                row = [s.id, s.name] + ["" if g is None else g for g in padded]
                writer.writerow(row)
        os.replace(tmp_path, path)
    except OSError as exc:
        raise FileAccessError(f"Не удалось записать файл {path}: {exc}") from exc


def export_top_n_csv(path: str, students: List[Student]) -> None:
    directory = os.path.dirname(path)
    if directory:
        os.makedirs(directory, exist_ok=True)
    try:
        with open(path, "w", encoding=ENCODING, newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["id", "name", "average", "grades"])
            for s in students:
                writer.writerow([s.id, s.name, f"{s.average:.2f}", s.grades_display()])
    except OSError as exc:
        raise FileAccessError(f"Не удалось записать файл {path}: {exc}") from exc
