"""Configuration classes and parser as well as manim-eng's default configuration."""

import dataclasses as dc
import re
from collections import defaultdict
from typing import Any, Self

import manim as mn
import numpy as np

STRING_TO_MANIM_COLOUR = {
    "white": mn.WHITE,
    "gray_a": mn.GRAY_A,
    "grey_a": mn.GREY_A,
    "gray_b": mn.GRAY_B,
    "grey_b": mn.GREY_B,
    "gray_c": mn.GRAY_C,
    "grey_c": mn.GREY_C,
    "gray_d": mn.GRAY_D,
    "grey_d": mn.GREY_D,
    "gray_e": mn.GRAY_E,
    "grey_e": mn.GREY_E,
    "black": mn.BLACK,
    "lighter_gray": mn.LIGHTER_GRAY,
    "lighter_grey": mn.LIGHTER_GREY,
    "light_gray": mn.LIGHT_GRAY,
    "light_grey": mn.LIGHT_GREY,
    "gray": mn.GRAY,
    "grey": mn.GREY,
    "dark_gray": mn.DARK_GRAY,
    "dark_grey": mn.DARK_GREY,
    "darker_gray": mn.DARKER_GRAY,
    "darker_grey": mn.DARKER_GREY,
    "blue_a": mn.BLUE_A,
    "blue_b": mn.BLUE_B,
    "blue_c": mn.BLUE_C,
    "blue_d": mn.BLUE_D,
    "blue_e": mn.BLUE_E,
    "pure_blue": mn.PURE_BLUE,
    "blue": mn.BLUE,
    "dark_blue": mn.DARK_BLUE,
    "teal_a": mn.TEAL_A,
    "teal_b": mn.TEAL_B,
    "teal_c": mn.TEAL_C,
    "teal_d": mn.TEAL_D,
    "teal_e": mn.TEAL_E,
    "teal": mn.TEAL,
    "green_a": mn.GREEN_A,
    "green_b": mn.GREEN_B,
    "green_c": mn.GREEN_C,
    "green_d": mn.GREEN_D,
    "green_e": mn.GREEN_E,
    "pure_green": mn.PURE_GREEN,
    "green": mn.GREEN,
    "yellow_a": mn.YELLOW_A,
    "yellow_b": mn.YELLOW_B,
    "yellow_c": mn.YELLOW_C,
    "yellow_d": mn.YELLOW_D,
    "yellow_e": mn.YELLOW_E,
    "yellow": mn.YELLOW,
    "gold_a": mn.GOLD_A,
    "gold_b": mn.GOLD_B,
    "gold_c": mn.GOLD_C,
    "gold_d": mn.GOLD_D,
    "gold_e": mn.GOLD_E,
    "gold": mn.GOLD,
    "red_a": mn.RED_A,
    "red_b": mn.RED_B,
    "red_c": mn.RED_C,
    "red_d": mn.RED_D,
    "red_e": mn.RED_E,
    "pure_red": mn.PURE_RED,
    "red": mn.RED,
    "maroon_a": mn.MAROON_A,
    "maroon_b": mn.MAROON_B,
    "maroon_c": mn.MAROON_C,
    "maroon_d": mn.MAROON_D,
    "maroon_e": mn.MAROON_E,
    "maroon": mn.MAROON,
    "purple_a": mn.PURPLE_A,
    "purple_b": mn.PURPLE_B,
    "purple_c": mn.PURPLE_C,
    "purple_d": mn.PURPLE_D,
    "purple_e": mn.PURPLE_E,
    "purple": mn.PURPLE,
    "pink": mn.PINK,
    "light_pink": mn.LIGHT_PINK,
    "orange": mn.ORANGE,
    "light_brown": mn.LIGHT_BROWN,
    "dark_brown": mn.DARK_BROWN,
    "gray_brown": mn.GRAY_BROWN,
    "grey_brown": mn.GREY_BROWN,
    "logo_white": mn.LOGO_WHITE,
    "logo_green": mn.LOGO_GREEN,
    "logo_blue": mn.LOGO_BLUE,
    "logo_red": mn.LOGO_RED,
    "logo_black": mn.LOGO_BLACK,
}


class ConfigBase:
    """Base class for manim-eng configuration classes."""

    def load_from_dict(
        self, dictionary: dict[str, Any], table_prefix: str = ""
    ) -> Self:
        r"""Load configuration in from a ``dict`` representation.

        Parameters
        ----------
        dictionary : dict[str, Any]
            The ``dict`` from which to load the values.
        table_prefix : str
            The current TOML table the dictionary values are a representation of. Allows
            this method to produce error messages that reflect the structure of the
            TOML from which the ``dict`` was generated.

        Notes
        -----
        This method is written as a strict intermediary between the configuration TOML
        file and the configuration classes. As such, an input of an empty dictionary
        ``{}`` will do nothing, as it is the equivalent of reading in an empty
        configuration file. The same goes for empty ``dict``\ s as values for tables: no
        change will be made to the table in this case.
        """
        possible_keys = self.__dict__.keys()

        for key, value in dictionary.items():
            if key not in possible_keys:
                raise ValueError(
                    f"Invalid {'table' if isinstance(value, dict) else 'key'} "
                    f"in manim-eng configuration: `{table_prefix}{key}`"
                )
            current_value = getattr(self, key)

            if isinstance(value, dict):
                # In this case, we have encountered a table.
                # First, check that this is a valid table.
                if not isinstance(current_value, ConfigBase):
                    raise ValueError(
                        f"Invalid table in manim-eng configuration: "
                        f"`{table_prefix}{key}`"
                    )
                # If it is, we call `load_from_dict` on the instance of ConfigBase that
                # represents the table.
                setattr(
                    self,
                    key,
                    type(current_value).load_from_dict(
                        current_value, value, table_prefix=f"{table_prefix}{key}."
                    ),
                )
                continue

            if isinstance(current_value, mn.ManimColor):
                if isinstance(value, mn.ManimColor):
                    setattr(self, key, value)
                    continue
                if not isinstance(value, str):
                    raise ValueError(
                        f"Invalid type in manim-eng configuration for key "
                        f"`{table_prefix}{key}`: "
                        f"{self._get_toml_type_from_python_variable(value)} "
                        f"(expected string)"
                    )
                if value not in STRING_TO_MANIM_COLOUR:
                    if not re.match(r"^#[0-9A-Fa-f]{6}$", value):
                        raise ValueError(
                            f"Invalid colour in manim-eng configuration "
                            f"for key `{table_prefix}{key}`: "
                            f"{value}"
                        )
                    setattr(self, key, mn.ManimColor(value))
                    continue
                setattr(self, key, STRING_TO_MANIM_COLOUR[value])
                continue

            if not isinstance(value, type(current_value)):
                raise ValueError(
                    f"Invalid type in manim-eng configuration for key "
                    f"`{table_prefix}{key}`: "
                    f"{self._get_toml_type_from_python_variable(value)} "
                    f"(expected "
                    f"{self._get_toml_type_from_python_variable(current_value)}"
                    f")"
                )

            setattr(self, key, value)

        return self

    def as_dict(self) -> dict[str, Any]:
        """Return this configuration as a dictionary.

        Returns
        -------
        dict[str, Any]
            This configuration as a dictionary, with subconfigurations being added as
            subdictionaries.
        """
        dictionary = self.__dict__
        for key, value in dictionary.items():
            if isinstance(value, ConfigBase):
                dictionary[key] = value.as_dict()
        return dictionary

    @staticmethod
    def _get_toml_type_from_python_variable(variable: Any) -> str:
        """Return the TOML type a Python variable would be stored as.

        Returns the TOML type that a Python value would've had if it were read from a
        manim-eng TOML configuration file. Serves to allow ``load_from_dict()`` to
        produce error messages relevant to the TOML the user wrote, rather than the
        internal Python representation of it.

        This is (roughly) an inversion of the table in the `tomllib docs <https://docs.python.org/3/library/tomllib.html#conversion-table>`_.
        """
        type_name = type(variable).__name__
        conversion_table = defaultdict(
            lambda: "table",
            {
                "str": "string",
                "int": "integer",
                "float": "float",
                "bool": "boolean",
                "list": "array",
                "dict": "table",
                "ManimColor": "string",
            },
        )
        return conversion_table[type_name]


@dc.dataclass
class ComponentSymbolConfig(ConfigBase):
    """Component display and behaviour configuration."""

    bipole_height: float = 0.4
    """The standard height to use for box-esque bipoles, such as resistors and fuses."""
    bipole_width: float = 1.0
    """The standard width to use for box-esque bipoles, such as resistors and fuses."""
    square_bipole_side_length: float = 1.5 * bipole_height
    """The standard height to use for bipoles with square bounding boxes, such as
    voltage sources and sensors."""
    component_stroke_width: float = mn.DEFAULT_STROKE_WIDTH
    """The stroke width to use for the component symbols."""
    current_arrow_radius: float = (2 / np.sqrt(3)) * 0.2 * bipole_height
    """The length from the centre of the current arrow triangle from its centre to one
    of its vertices."""
    terminal_length: float = 0.4 * bipole_width
    """The length of the terminal of a component."""
    wire_stroke_width: float = 0.625 * component_stroke_width
    """The stroke width to use for wires."""
    mark_font_size: float = 36.0
    """The default font size to use for marks (e.g. labels and annotations)."""
    mark_cardinal_alignment_margin: float = 5 * mn.DEGREES
    """The maximum angle a component can be from one of horizontal or vertical whilst
    still being considered horizontal or vertical for the purpose of mark alignment."""
    arrow_stroke_width: float = wire_stroke_width
    """The stroke width to use for arrows in voltage marks and similar."""
    arrow_tip_length: float = 0.2
    """The length of voltage arrow tips."""
    voltage_default_angle: float = 60 * mn.DEGREES
    """The angle a voltage arrow will sweep with no other reference provided."""
    node_radius: float = 0.06
    """The radius of wire nodes."""
    variability_arrow_tip_length: float = 0.125
    """The length of arrow tips in arrows signifying variability in a component."""
    monopole_width: float = 0.5 * bipole_width
    """The width of monopole source/ground symbols."""
    plate_gap: float = bipole_width / 6
    """The gap between plates of plated components (i.e. capacitors and cells)."""
    plate_height: float = 5 * plate_gap
    """The height of plates of plated components (i.e. capacitors and cells)."""


@dc.dataclass
class AnchorDisplayConfig(ConfigBase):
    """Anchor debug display configuration."""

    annotation_colour: mn.ManimColor = dc.field(default_factory=lambda: mn.BLUE)
    """The colour to use for annotation anchors' debug visuals. Defaults to blue."""
    centre_colour: mn.ManimColor = dc.field(default_factory=lambda: mn.PURPLE)
    """The colour to use for centre anchors' debug visuals. Defaults to purple."""
    current_colour: mn.ManimColor = dc.field(default_factory=lambda: mn.ORANGE)
    """The colour to use for current anchors' debug visuals. Defaults to orange."""
    label_colour: mn.ManimColor = dc.field(default_factory=lambda: mn.RED)
    """The colour to use for label anchors' debug visuals. Defaults to red."""
    radius: float = 0.06
    """The radius of anchor visualisation rings."""
    stroke_width: float = 2.0
    """The stroke width of anchor visualisation rings."""
    terminal_colour: mn.ManimColor = dc.field(default_factory=lambda: mn.GREEN)
    """The colour to use for terminal anchors' debug visuals. Defaults to green."""
    voltage_colour: mn.ManimColor = dc.field(default_factory=lambda: mn.YELLOW)
    """The colour to use for voltage anchors' debug visuals. Defaults to yellow."""


@dc.dataclass
class ManimEngConfig(ConfigBase):
    """manim-eng configuration."""

    anchor: AnchorDisplayConfig = dc.field(default_factory=AnchorDisplayConfig)
    """Anchor debug display subconfig."""
    debug: bool = False
    """Whether or not to display debug information."""
    symbol: ComponentSymbolConfig = dc.field(default_factory=ComponentSymbolConfig)
    """Component symbol subconfig."""
