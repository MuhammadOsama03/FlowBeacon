from app import dependencies


def test_store_is_shared_and_configurable(monkeypatch, tmp_path):
    monkeypatch.setenv("FLOWBEACON_DATABASE_PATH", str(tmp_path / "runtime.db"))
    dependencies.reset_dependencies()

    first = dependencies.get_store()
    second = dependencies.get_store()

    assert first is second
    assert first.database_path == str(tmp_path / "runtime.db")
    assert dependencies.get_ingestor().store is first
    dependencies.reset_dependencies()

