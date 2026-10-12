from lab.main import main


def test_cli_add_show_and_exit(tmp_path, monkeypatch, capsys):
    """Минимальный сценарий: добавить студента, показать список, выйти,
    сохранить в CSV через аргумент --save."""
    out_path = tmp_path / "out.csv"

    inputs = iter(
        [
            "4",  # добавить студента
            "1",  # id
            "Иванов Иван",  # ФИО
            "80 90 100",  # оценки
            "3",  # показать всех
            "0",  # выход
        ]
    )
    monkeypatch.setattr("builtins.input", lambda _prompt="": next(inputs))

    exit_code = main(["--save", str(out_path)])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "Студент добавлен" in captured.out
    assert "Иванов Иван" in captured.out
    assert out_path.exists()
    assert "1,Иванов Иван,80,90,100" in out_path.read_text(encoding="utf-8")


def test_cli_invalid_menu_choice_does_not_crash(monkeypatch, capsys):
    inputs = iter(["999", "0"])
    monkeypatch.setattr("builtins.input", lambda _prompt="": next(inputs))

    exit_code = main([])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "Неизвестный пункт меню" in captured.out


def test_cli_remove_missing_student_shows_error_not_crash(monkeypatch, capsys):
    inputs = iter(["5", "999", "0"]) 
    monkeypatch.setattr("builtins.input", lambda _prompt="": next(inputs))

    exit_code = main([])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "Ошибка" in captured.out


def test_cli_top_flag_loads_and_prints(tmp_path, capsys):
    csv_path = tmp_path / "students.csv"
    csv_path.write_text(
        "id,name,grade1,grade2\n1,A,50,60\n2,B,90,100\n",
        encoding="utf-8",
    )

    exit_code = main(["--load", str(csv_path), "--top", "1"])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "B" in captured.out
    assert "A" not in captured.out.split("\n")[-3]  


def test_cli_autosave_writes_csv_after_each_change(tmp_path, monkeypatch):
    csv_path = tmp_path / "students.csv"
    csv_path.write_text("id,name,grade1\n1,Иванов Иван,80\n", encoding="utf-8")
    inputs = iter(["4", "2", "Новый Студент", "50", "0"])
    monkeypatch.setattr("builtins.input", lambda _prompt="": next(inputs))

    assert main(["--load", str(csv_path), "--autosave"]) == 0
    assert "2,Новый Студент,50" in csv_path.read_text(encoding="utf-8")
