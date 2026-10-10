import json
import threading
import urllib.error
import urllib.request

import pytest

from lab import web
from lab.models import Student


@pytest.fixture
def base_url():
    web.STATE.students = [Student(1, "Иванов Иван", [80, 90]), Student(2, "Петров Петр", [50])]
    server = web.make_server(0)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    yield f"http://127.0.0.1:{server.server_address[1]}"
    server.shutdown()
    server.server_close()


def call(method, url, body=None):
    data = json.dumps(body).encode("utf-8") if body is not None else None
    req = urllib.request.Request(url, data=data, method=method, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req) as resp:
            return resp.status, json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        return exc.code, json.loads(exc.read().decode("utf-8"))


def test_list_sorted_by_avg(base_url):
    status, data = call("GET", base_url + "/api/students?sort=avg")
    assert status == 200
    assert [s["id"] for s in data] == [1, 2]


def test_add_and_delete(base_url):
    status, _ = call("POST", base_url + "/api/students", {"id": 3, "name": "Новый", "grades": "70 -"})
    assert status == 201
    status, _ = call("DELETE", base_url + "/api/students/3")
    assert status == 200


def test_duplicate_returns_400(base_url):
    status, data = call("POST", base_url + "/api/students", {"id": 1, "name": "Дубль", "grades": ""})
    assert status == 400
    assert "error" in data


def test_invalid_grade_returns_400(base_url):
    status, _ = call("POST", base_url + "/api/students", {"id": 9, "name": "X", "grades": "abc"})
    assert status == 400


def test_stats(base_url):
    status, data = call("GET", base_url + "/api/stats")
    assert status == 200 and data["count"] == 2
