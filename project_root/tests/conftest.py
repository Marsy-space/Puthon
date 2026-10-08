import sys
from pathlib import Path

import pytest

# Гарантируем, что пакет lab импортируется из корня проекта
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from lab.models import Student  # noqa: E402


@pytest.fixture
def sample_students():
    return [
        Student(id=1, name="Иванов Иван", grades=[78, 85, 90]),
        Student(id=2, name="Иванов Петр", grades=[65, 70, 0]),
        Student(id=3, name="Иванова Анна", grades=[92, 88, 95]),
        Student(id=4, name="Иванов Олег", grades=[100, 90, None]),
        Student(id=5, name="Иванова Юлия", grades=[80, None, None]),
    ]
