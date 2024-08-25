import os
from typing import Any

import tomllib


class UnsupportedOsTypeError(RuntimeError):
    pass


def get_user_config() -> dict[str, Any]:
    r"""Load the user-level configuration into a dictionary.

    Loads the user-level configuration out of ``~/.config/manim/manim-eng.toml`` (on
    Linux and macOS) or ``~\AppData\Roaming\Manim\manim-eng.toml`` (on Windows) into a
    nested dictionary.

    Returns
    -------
    dict[str, Any]
        A dictionary representation of the TOML file. If the file cannot be found,
        returns an empty dictionary.
    """
    home_directory = os.path.expanduser("~")
    config_directory: str

    # Get the location of the Manim configuration directory, as per
    # https://docs.manim.community/en/stable/guides/configuration.html#the-user-config-file
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
            config_from_file = tomllib.load(filehandle)
    except OSError:
        return {}

    return config_from_file
