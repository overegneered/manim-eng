"""Configuration readers for parsing TOML config files to Python dictionaries."""

import os
import tomllib
from typing import Any


class UnsupportedOsTypeError(RuntimeError):
    pass


def get_user_config() -> dict[str, Any]:
    r"""Load the user-level configuration into a dictionary.

    Loads the user-level configuration out of ``~/.config/manim/manim-eng.toml`` (on
    Linux and macOS) or ``~\AppData\Roaming\Manim\manim-eng.toml`` (on Windows) into a
    nested dictionary. The directory containing ``manim-eng.toml`` is as outlined in the
    `Manim docs <https://docs.manim.community/en/stable/guides/configuration.html#the-user-config-file>`_.

    Returns
    -------
    dict[str, Any]
        A dictionary representation of the TOML file. If the file cannot be found,
        returns an empty dictionary ``{}``.
    """
    home_directory = os.path.expanduser("~")
    config_directory: str

    match os.name:
        case "posix":
            config_directory = home_directory + "/.config/manim"
        case "nt":
            config_directory = home_directory + "/AppData/Roaming/Manim"
        case other:
            raise UnsupportedOsTypeError(f"Unsupported/unknown OS type '{other}'.")

    config_file = config_directory + "/manim-eng.toml"

    try:
        with open(config_file, "rb") as filehandle:
            return tomllib.load(filehandle)
    except OSError:
        return {}


def get_project_config() -> dict[str, Any]:
    """Load the project-level configuration from the working directory.

    Returns
    -------
    dict[str, Any]
        A dictionary representation of the TOML file. If the file cannot be found,
        returns an empty dictionary ``{}``.
    """
    config_file = os.getcwd() + "/manim-eng.toml"
    try:
        with open(config_file, "rb") as filehandle:
            return tomllib.load(filehandle)
    except OSError:
        return {}
