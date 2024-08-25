import dataclasses as dc
from collections import defaultdict
from typing import Any, Self

import manim as mn
import numpy as np


class ConfigBase:
    """Base class for manim-eng configuration classes."""

    def load_from_dict(
        self, dictionary: dict[str, Any], table_prefix: str = ""
    ) -> Self:
        """Load configuration in from a ``dict`` representation.

        Parameters
        ----------
        dictionary : dict[str, Any]
            The ``dict`` from which to load the values.
        table_prefix : str
            The current TOML table the dictionary values are a representation of. Allows
            this method to produce error messages that reflect the structure of the
            TOML from which the ``dict`` was generated.

        Returns
        -------
        Self
            The (modified) config object on which it was called.

        Notes
        -----
        This method is written as a strict intermediary between the configuration TOML
        file and the configuration classes. As such, an input of an empty dictionary
        ``{}`` will do nothing, as it is the equivalent of reading in an empty
        configuration file. The same goes for empty ``dict``s as values for tables: no
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

            if not isinstance(value, type(current_value)):
                raise ValueError(
                    f"Invalid type in manim-eng configuration for key "
                    f"`{table_prefix}{key}`: "
                    f"{self.get_toml_type_from_python_variable(value)} "
                    f"(expected "
                    f"{self.get_toml_type_from_python_variable(current_value)}"
                    f")"
                )

            setattr(self, key, value)

        return self

    @staticmethod
    def get_toml_type_from_python_variable(variable: Any) -> str:
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
    component_stroke_width: float = mn.DEFAULT_STROKE_WIDTH
    """The stroke width to use for the component symbols."""
    current_arrow_radius: float = (2 / np.sqrt(3)) * 0.2 * bipole_height
    """The length from the centre of the current arrow triangle from its centre to one
    of its vertices."""
    mark_font_size: float = 36.0
    """The default font size to use for marks (e.g. labels and annotations)."""
    mark_cardinal_alignment_margin: float = 5 * (mn.PI / 180)
    """The maximum angle a component can be from one of horizontal or vertical whilst
    still being considered horizontal or vertical for the purpose of mark alignment."""
    terminal_length: float = 0.5 * bipole_width
    """The length of the terminal of a component."""
    wire_stroke_width: float = 0.625 * component_stroke_width
    """The stroke width to use for wires."""


@dc.dataclass
class AnchorDisplayConfig(ConfigBase):
    """Anchor debug display configuration."""

    annotation_colour: mn.ManimColor = dc.field(default_factory=lambda: mn.BLUE)
    """The colour to use for annotation anchors' debug visuals."""
    centre_colour: mn.ManimColor = dc.field(default_factory=lambda: mn.PURPLE)
    """The colour to use for centre anchors' debug visuals."""
    current_colour: mn.ManimColor = dc.field(default_factory=lambda: mn.ORANGE)
    """The colour to use for current anchors' debug visuals."""
    label_colour: mn.ManimColor = dc.field(default_factory=lambda: mn.RED)
    """The colour to use for label anchors' debug visuals."""
    radius: float = 0.06
    """The radius of anchor visualisation rings."""
    stroke_width: float = 2.0
    """The stroke width of anchor visualisation rings."""
    terminal_colour: mn.ManimColor = dc.field(default_factory=lambda: mn.GREEN)
    """The colour to use for terminal anchors' debug visuals."""


@dc.dataclass
class ManimEngConfig(ConfigBase):
    """manim-eng configuration."""

    anchor: AnchorDisplayConfig = dc.field(default_factory=AnchorDisplayConfig)
    """Anchor debug display subconfig."""
    debug: bool = False
    """Whether or not to display debug information."""
    symbol: ComponentSymbolConfig = dc.field(default_factory=ComponentSymbolConfig)
    """Component symbol subconfig."""
