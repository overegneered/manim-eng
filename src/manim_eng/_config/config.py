import dataclasses as dc

import manim as mn


@dc.dataclass
class ComponentSymbolConfig:
    """Component display and behaviour configuration."""

    component_stroke_width: float = mn.DEFAULT_STROKE_WIDTH
    """The stroke width to use for the component symbols."""
    mark_font_size: float = 36.0
    """The default font size to use for marks (e.g. labels and annotations)."""
    mark_cardinal_alignment_margin: float = 5 * (mn.PI / 180)
    """The maximum angle a component can be from one of horizontal or vertical whilst
    still being considered horizontal or vertical for the purpose of mark alignment."""
    wire_stroke_width: float = 0.625 * component_stroke_width
    """The stroke width to use for wires."""


@dc.dataclass
class AnchorColourConfig:
    """Anchor colour configuration."""

    annotation: mn.ManimColor = dc.field(default_factory=lambda: mn.BLUE)
    """The colour to use for annotation anchors' debug visuals."""
    centre: mn.ManimColor = dc.field(default_factory=lambda: mn.PURPLE)
    """The colour to use for centre anchors' debug visuals."""
    current: mn.ManimColor = dc.field(default_factory=lambda: mn.ORANGE)
    """The colour to use for current anchors' debug visuals."""
    label: mn.ManimColor = dc.field(default_factory=lambda: mn.RED)
    """The colour to use for label anchors' debug visuals."""
    terminal: mn.ManimColor = dc.field(default_factory=lambda: mn.GREEN)
    """The colour to use for terminal anchors' debug visuals."""


@dc.dataclass
class ManimEngConfig:
    """manim-eng configuration."""

    anchor_colour: AnchorColourConfig = dc.field(default_factory=AnchorColourConfig)
    """Anchor colours subconfig."""
    debug: bool = False
    """Whether or not to display debug information."""
    symbol: ComponentSymbolConfig = dc.field(default_factory=ComponentSymbolConfig)
    """Component symbol subconfig."""
