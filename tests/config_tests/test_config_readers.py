import os
from unittest import mock

import pytest
from manim_eng._config.config_readers import (
    UnsupportedOsTypeError,
    get_project_config,
    get_user_config,
)


def replace_os_path_expanduser(path: str) -> str:
    if path == "~":
        return "USERHOME"
    return os.path.expanduser(path)


@mock.patch("os.name", "posix")
@mock.patch("tomllib.load", return_value={})
@mock.patch("os.path.expanduser", replace_os_path_expanduser)
@mock.patch("builtins.open")
def test_get_user_config_config_file_correct_path_posix(
    open_mocked: mock.MagicMock,
    _tomllib_load_mocked: mock.MagicMock,  # noqa: PT019
) -> None:
    _ = get_user_config()

    open_mocked.assert_called_with("USERHOME/.config/manim/manim-eng.toml", "rb")


@mock.patch("os.name", "nt")
@mock.patch("tomllib.load", return_value={})
@mock.patch("os.path.expanduser", replace_os_path_expanduser)
@mock.patch("builtins.open")
def test_get_user_config_config_file_correct_path_windows(
    open_mocked: mock.MagicMock,
    _tomllib_load_mocked: mock.MagicMock,  # noqa: PT019
) -> None:
    _ = get_user_config()

    open_mocked.assert_called_once_with(
        "USERHOME/AppData/Roaming/Manim/manim-eng.toml", "rb"
    )


@mock.patch("os.name", "not a valid os name")
def test_get_user_config_config_file_throws_error_if_os_name_not_posix_or_nt() -> None:
    with pytest.raises(
        UnsupportedOsTypeError,
        match="Unsupported/unknown OS type 'not a valid os name'.",
    ):
        _ = get_user_config()


@mock.patch("builtins.open", side_effect=OSError)
def test_get_user_config_file_not_found_returns_empty_dict(
    _open_mocked: mock.MagicMock,  # noqa: PT019
) -> None:
    result = get_user_config()

    assert result == {}


@mock.patch("os.getcwd", return_value="CWD")
@mock.patch("tomllib.load", return_value={})
@mock.patch("builtins.open")
def test_get_project_config_attempts_to_open_the_correct_file(
    open_mocked: mock.MagicMock,
    _tomllib_load_mocked: mock.MagicMock,  # noqa: PT019
    _os_getcwd_mocked: mock.MagicMock,  # noqa: PT019
) -> None:
    get_project_config()

    open_mocked.assert_called_once_with("CWD/manim-eng.toml", "rb")


@mock.patch("builtins.open", side_effect=OSError)
def test_get_project_config_file_not_found_returns_empty_dict(
    _open_mocked: mock.MagicMock,  # noqa: PT019
) -> None:
    result = get_project_config()

    assert result == {}
