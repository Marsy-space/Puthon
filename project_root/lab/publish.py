"""Публикация данных для сайта: CSV -> статичный файл site/data.json.

Сайт на CDN только читает data.json. Менять данные можно только здесь
(правите CSV или работаете через CLI), затем запускаете публикацию.
Файл перезаписывается ТОЛЬКО если данные реально изменились.

Запуск:
    python -m lab.publish
    python -m lab.publish --csv data/students.csv --out site/data.json
"""

import argparse
import hashlib
import json
import os
import sys
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from lab.errors import FileAccessError, LabError  # noqa: E402
from lab.io_utils import read_students_csv  # noqa: E402
from lab.models import Student  # noqa: E402
from lab.processing import group_stats, sort_students  # noqa: E402


def _student_dict(s: Student) -> Dict[str, Any]:
    return {"id": s.id, "name": s.name, "grades": s.grades, "average": round(s.average, 2)}


def build_snapshot(students: List[Student]) -> Dict[str, Any]:
    """Собирает снимок данных. version - хэш содержимого: меняется
    только когда меняются сами данные (а не время публикации)."""
    st = group_stats(students)
    payload = {
        "students": [_student_dict(s) for s in sort_students(students, key="id")],
        "stats": {
            "count": st["count"],
            "overall_avg": round(st["overall_avg"], 2),
            "best": _student_dict(st["best"]) if st["best"] else None,
            "worst": _student_dict(st["worst"]) if st["worst"] else None,
        },
    }
    raw = json.dumps(payload, sort_keys=True, ensure_ascii=False).encode("utf-8")
    version = hashlib.sha256(raw).hexdigest()[:12]
    generated = datetime.now(timezone.utc).isoformat(timespec="seconds")
    return {"version": version, "generated_at": generated, **payload}


def _current_version(out_path: str) -> Optional[str]:
    try:
        with open(out_path, "r", encoding="utf-8") as f:
            return json.load(f).get("version")
    except (OSError, ValueError, AttributeError):
        return None


def publish(csv_path: str, out_path: str) -> bool:
    """Читает CSV и обновляет data.json. Возвращает True, если файл записан,
    False - если данные не изменились. Ошибки CSV/файлов - LabError."""
    snapshot = build_snapshot(read_students_csv(csv_path))
    if snapshot["version"] == _current_version(out_path):
        return False
    directory = os.path.dirname(out_path)
    if directory:
        os.makedirs(directory, exist_ok=True)
    try:
        with open(out_path, "w", encoding="utf-8", newline="\n") as f:
            json.dump(snapshot, f, ensure_ascii=False, indent=2)
    except OSError as exc:
        raise FileAccessError(f"Не удалось записать {out_path}: {exc}") from exc
    return True


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Опубликовать данные студентов для сайта")
    parser.add_argument("--csv", default=os.path.join(_PROJECT_ROOT, "data", "students.csv"))
    parser.add_argument("--out", default=os.path.join(_PROJECT_ROOT, "site", "data.json"))
    args = parser.parse_args(argv)
    try:
        changed = publish(args.csv, args.out)
    except LabError as exc:
        print(f"Ошибка: {exc}")
        return 1
    print(f"Данные обновлены: {args.out}" if changed else "Данные не изменились, файл не тронут.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
