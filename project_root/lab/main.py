"""Консольное приложение для управления списком студентов и их оценок.

Запуск:
    python -m lab.main
"""

import argparse
import os
import sys
from typing import List, Optional

_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from lab.errors import LabError
from lab.io_utils import export_top_n_csv, read_students_csv, write_students_csv
from lab.models import Student, validate_grade, validate_id, validate_name
from lab.processing import (
    VALID_SORT_KEYS,
    add_student,
    group_stats,
    remove_student,
    sort_students,
    top_n,
    update_grades,
)

MENU_TEXT = """
==== Меню ====
1. Загрузить студентов из CSV
2. Сохранить студентов в CSV
3. Показать всех студентов
4. Добавить студента
5. Удалить студента по id
6. Обновить оценки студента по id
7. Показать статистику по группе
8. Экспортировать ТОП-N студентов в CSV
9. Отсортировать и показать (avg/name/id)
0. Выход
"""


def print_students(students: List[Student]) -> None:
    if not students:
        print("Список студентов пуст.")
        return
    print(f"{'id':<5}{'ФИО':<25}{'Оценки':<20}{'Средний балл':>12}")
    for s in students:
        print(f"{s.id:<5}{s.name:<25}{s.grades_display():<20}{s.average:>12.2f}")


def prompt(text: str) -> str:
    return input(text).strip()


def action_load(students: List[Student]) -> List[Student]:
    path = prompt("Путь к CSV-файлу для загрузки: ")
    loaded = read_students_csv(path)
    print(f"Загружено студентов: {len(loaded)}")
    return loaded


def action_save(students: List[Student]) -> None:
    path = prompt("Путь к CSV-файлу для сохранения: ")
    write_students_csv(path, students, with_header=True)
    print(f"Сохранено в {path}")


def action_add(students: List[Student]) -> None:
    sid = validate_id(prompt("id: "))
    name = validate_name(prompt("ФИО: "))
    raw_grades = prompt("Оценки через пробел (можно пусто): ")
    grades = [validate_grade(g) for g in raw_grades.split()] if raw_grades else []
    add_student(students, Student(id=sid, name=name, grades=grades))
    print("Студент добавлен.")


def action_remove(students: List[Student]) -> None:
    sid = validate_id(prompt("id студента для удаления: "))
    remove_student(students, sid)
    print("Студент удалён.")


def action_update_grades(students: List[Student]) -> None:
    sid = validate_id(prompt("id студента: "))
    raw_grades = prompt("Новые оценки через пробел (можно пусто): ")
    grades = [validate_grade(g) for g in raw_grades.split()] if raw_grades else []
    update_grades(students, sid, grades)
    print("Оценки обновлены.")


def action_stats(students: List[Student]) -> None:
    stats = group_stats(students)
    print(f"Количество студентов: {stats['count']}")
    print(f"Общий средний балл по группе: {stats['overall_avg']:.2f}")
    best, worst = stats["best"], stats["worst"]
    if best is not None:
        print(f"Лучший студент: {best.name} (id={best.id}, avg={best.average:.2f})")
        print(f"Худший студент: {worst.name} (id={worst.id}, avg={worst.average:.2f})")
    else:
        print("Нет данных для определения лучшего/худшего студента.")


def action_export_top(students: List[Student]) -> None:
    n = validate_id(prompt("N (сколько студентов взять): "))
    path = prompt("Путь для сохранения ТОП-N CSV: ")
    winners = top_n(students, n)
    export_top_n_csv(path, winners)
    print(f"Экспортировано {len(winners)} студентов в {path}")


def action_sort_and_show(students: List[Student]) -> None:
    key = prompt(f"Ключ сортировки {VALID_SORT_KEYS}: ").strip().lower()
    print_students(sort_students(students, key=key))


def autosave(students: List[Student], path: Optional[str]) -> None:
    """Если включён --autosave, сразу записывает изменения в CSV."""
    if path:
        write_students_csv(path, students, with_header=True)
        print(f"Автосохранение: {path}")


def run_menu(students: List[Student], autosave_path: Optional[str] = None) -> None:
    while True:
        print(MENU_TEXT)
        choice = prompt("Выберите пункт меню: ")
        try:
            if choice == "1":
                students = action_load(students)
            elif choice == "2":
                action_save(students)
            elif choice == "3":
                print_students(students)
            elif choice == "4":
                action_add(students)
                autosave(students, autosave_path)
            elif choice == "5":
                action_remove(students)
                autosave(students, autosave_path)
            elif choice == "6":
                action_update_grades(students)
                autosave(students, autosave_path)
            elif choice == "7":
                action_stats(students)
            elif choice == "8":
                action_export_top(students)
            elif choice == "9":
                action_sort_and_show(students)
            elif choice == "0":
                print("Выход из программы.")
                return
            else:
                print("Неизвестный пункт меню, попробуйте снова.")
        except LabError as exc:
            print(f"Ошибка: {exc}")
        except Exception as exc:  
            print(f"Непредвиденная ошибка: {exc}")


def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Управление списком студентов и оценок (CSV)")
    parser.add_argument("--load", metavar="PATH", help="загрузить студентов из CSV при старте")
    parser.add_argument("--save", metavar="PATH", help="сохранить студентов в CSV перед выходом")
    parser.add_argument("--autosave", action="store_true", help="сохранять в файл из --load после каждого изменения")
    parser.add_argument("--top", metavar="N", type=int, help="вывести ТОП-N студентов и выйти")
    return parser.parse_args(argv)


def main(argv: Optional[List[str]] = None) -> int:
    args = parse_args(argv)
    students: List[Student] = []

    if args.load:
        try:
            students = read_students_csv(args.load)
            print(f"Загружено студентов: {len(students)}")
        except LabError as exc:
            print(f"Ошибка загрузки: {exc}")
            return 1

    if args.top is not None:
        winners = top_n(students, args.top)
        print_students(winners)
        return 0

    if args.autosave and not args.load:
        print("--autosave работает только вместе с --load PATH")
        return 1

    run_menu(students, args.load if args.autosave else None)

    if args.save:
        try:
            write_students_csv(args.save, students, with_header=True)
            print(f"Сохранено в {args.save}")
        except LabError as exc:
            print(f"Ошибка сохранения: {exc}")
            return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
