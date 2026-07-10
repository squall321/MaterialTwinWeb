# 설정 DATA_DIR 해석 검증 — MATERIALTWIN > HEAX_DATA_DIR > 폴백, 빈 문자열 방어.
from __future__ import annotations

from pathlib import Path


def _fresh_settings(monkeypatch, **env):
    """env를 지정값으로 세팅하고 캐시 없이 Settings를 만든다."""
    for k in ("MATERIALTWIN_DATA_DIR", "MATERIALTWIN_DATABASE_URL", "HEAX_DATA_DIR"):
        monkeypatch.delenv(k, raising=False)
    for k, v in env.items():
        monkeypatch.setenv(k, v)
    from app.config import Settings
    return Settings()


def test_explicit_data_dir_wins(monkeypatch, tmp_path):
    s = _fresh_settings(monkeypatch, MATERIALTWIN_DATA_DIR=str(tmp_path / "explicit"))
    assert s.data_dir == (tmp_path / "explicit").resolve()


def test_heax_data_dir_fallback(monkeypatch, tmp_path):
    # MATERIALTWIN_DATA_DIR 없으면 런처 볼륨(HEAX_DATA_DIR)을 쓴다(D1).
    s = _fresh_settings(monkeypatch, HEAX_DATA_DIR=str(tmp_path / "heaxvol"))
    assert s.data_dir == (tmp_path / "heaxvol").resolve()


def test_empty_data_dir_does_not_leak_to_cwd(monkeypatch, tmp_path):
    # 빈 문자열(오설정)은 CWD로 새지 않고 HEAX 폴백을 태워야 한다(적대적 리뷰 회귀).
    s = _fresh_settings(monkeypatch,
                        MATERIALTWIN_DATA_DIR="",
                        HEAX_DATA_DIR=str(tmp_path / "heaxvol"))
    assert s.data_dir == (tmp_path / "heaxvol").resolve()
    assert s.data_dir != Path.cwd()


def test_empty_data_dir_no_heax_uses_dev_fallback(monkeypatch):
    # 빈 문자열 + HEAX도 없으면 개발 폴백(CWD 아님).
    s = _fresh_settings(monkeypatch, MATERIALTWIN_DATA_DIR="")
    assert s.data_dir != Path.cwd()
    assert s.data_dir.name == "data"  # backend/var/data


def test_database_url_derived_from_data_dir(monkeypatch, tmp_path):
    s = _fresh_settings(monkeypatch, MATERIALTWIN_DATA_DIR=str(tmp_path / "d"))
    assert s.database_url == f"sqlite:///{(tmp_path / 'd').resolve() / 'materialtwin.db'}"
