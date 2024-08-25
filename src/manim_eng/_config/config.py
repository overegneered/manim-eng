import dataclasses as dc

import manim as mn
import numpy as np


@dc.dataclass
class ComponentSymbolConfig:
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
class AnchorDisplayConfig:
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
    stroke_width: float = 2
    """The stroke width of anchor visualisation rings."""
    terminal_colour: mn.ManimColor = dc.field(default_factory=lambda: mn.GREEN)
    """The colour to use for terminal anchors' debug visuals."""


@dc.dataclass
class ManimEngConfig:
    """manim-eng configuration."""

    anchor: AnchorDisplayConfig = dc.field(default_factory=AnchorDisplayConfig)
    """Anchor debug display subconfig."""
    debug: bool = False
    """Whether or not to display debug information."""
    symbol: ComponentSymbolConfig = dc.field(default_factory=ComponentSymbolConfig)
    """Component symbol subconfig."""
