"""Component symbols for transistors."""

from typing import Any, Literal

import manim as mn
import numpy as np

from manim_eng import config_eng
from manim_eng.components.base.terminal import Terminal
from manim_eng.components.base.tripole import Tripole


class BaseBJT(Tripole):
    """Circuit symbol for a bipolar junction transistor with unspecified type."""

    def _construct(self, draw_emitter_line: bool = True) -> None:
        """Construct a basic bipolar junction transistor.

        Parameters
        ----------
        draw_be_line : bool
            Whether or not to draw the emitter line. Defaults to ``False``.
        """
        super()._construct()

        width = config_eng.symbol.tripole_width
        height = config_eng.symbol.tripole_height
        # horizontal line
        line_horizontal = mn.Line(
            np.array([-0.35 * width, 0.6 * height, 0.0]),
            np.array([0.35 * width, 0.6 * height, 0.0]),
        ).match_style(self)
        # vertical line from the base
        line_base = mn.Line(0.6 * height * mn.UP, height * mn.UP).match_style(self)
        # diagonal line from the collector
        line_collector = mn.Line(
            np.array([-0.5 * width, 0.0, 0.0]),
            np.array([-0.125 * width, 0.6 * height, 0.0]),
        ).match_style(self)
        self._body.add(line_horizontal, line_base, line_collector)

        # diagonal line from the emitter
        if draw_emitter_line:
            line_emitter = mn.Line(
                np.array([0.5 * width, 0.0, 0.0]),
                np.array([0.125 * width, 0.6 * height, 0.0]),
            ).match_style(self)
            self._body.add(line_emitter)

    @property
    def base(self) -> Terminal:
        """Return the base terminal of the transistor."""
        return self.top

    @property
    def collector(self) -> Terminal:
        """Return the collector terminal of the transistor."""
        return self.left

    @property
    def emitter(self) -> Terminal:
        """Return the emitter terminal of the transistor."""
        return self.right


class NPNTransistor(BaseBJT):
    """Circuit symbol for an NPN bipolar junction transistor."""

    def _construct(self) -> None:  # type: ignore[override]
        super()._construct(draw_emitter_line=False)

        width = config_eng.symbol.tripole_width
        height = config_eng.symbol.tripole_height
        # arrow
        arrow = mn.Arrow(
            start=np.array([0.125 * width, 0.6 * height, 0.0]),
            end=np.array([0.5 * width, 0.0, 0.0]),
            buff=0.0,
            stroke_width=self.stroke_width,
            fill_opacity=1.0,
            max_tip_length_to_length_ratio=config_eng.symbol.max_tip_length_to_length_ratio,
        )
        self._body.add(arrow)


class PNPTransistor(BaseBJT):
    """Circuit symbol for an NPN bipolar junction transistor."""

    def _construct(self) -> None:  # type: ignore[override]
        super()._construct(draw_emitter_line=False)

        width = config_eng.symbol.tripole_width
        height = config_eng.symbol.tripole_height
        # arrow
        arrow = mn.Arrow(
            start=np.array([0.5 * width, 0.0, 0.0]),
            end=np.array([0.125 * width, 0.6 * height, 0.0]),
            buff=0,
            stroke_width=self.stroke_width,
            fill_opacity=1.0,
            max_tip_length_to_length_ratio=config_eng.symbol.max_tip_length_to_length_ratio,
        )
        self._body.add(arrow)


class BaseJFET(Tripole):
    """Circuit symbol for a junction field effect transistor with unspecified type."""

    def _construct(self, draw_gate_line: bool = True) -> None:
        super()._construct()

        width = config_eng.symbol.tripole_width
        height = config_eng.symbol.tripole_height
        # horizontal line
        line_horizontal = mn.Line(
            np.array([-0.35 * width, 0.5 * height, 0.0]),
            np.array([0.35 * width, 0.5 * height, 0.0]),
        ).match_style(self)
        self._body.add(line_horizontal)
        # vertical line from the gate
        if draw_gate_line:
            line_gate = mn.Line(0.5 * height * mn.UP, height * mn.UP).match_style(self)
            self._body.add(line_gate)
        # lines from the source
        line_source = mn.VMobject()
        line_source.start_new_path(0.5 * width * mn.LEFT)
        line_source.add_line_to(0.25 * width * mn.LEFT)
        line_source.add_line_to(np.array([-0.25 * width, 0.5 * height, 0.0]))
        line_source.match_style(self)
        self._body.add(line_source)

        # lines from the drain
        line_drain = mn.VMobject()
        line_drain.start_new_path(0.5 * width * mn.RIGHT)
        line_drain.add_line_to(0.25 * width * mn.RIGHT)
        line_drain.add_line_to(np.array([0.25 * width, 0.5 * height, 0.0]))
        line_drain.match_style(self)
        self._body.add(line_drain)

    @property
    def gate(self) -> Terminal:
        """Return the gate terminal of the transistor."""
        return self.top

    @property
    def source(self) -> Terminal:
        """Return the source terminal of the transistor."""
        return self.left

    @property
    def drain(self) -> Terminal:
        """Return the drain terminal of the transistor."""
        return self.right


class NChannelJFET(BaseJFET):
    """Circuit symbol for an N-channel junction field effect transistor."""

    def _construct(self) -> None:  # type: ignore[override]
        super()._construct(draw_gate_line=False)

        height = config_eng.symbol.tripole_height
        # arrow pointing into the channel
        arrow = mn.Arrow(
            start=height * mn.UP,
            end=0.5 * height * mn.UP,
            buff=0.0,
            stroke_width=self.stroke_width,
            fill_opacity=1.0,
            max_tip_length_to_length_ratio=0.5,
            max_stroke_width_to_length_ratio=10.0,
        )
        self._body.add(arrow)


class PChannelJFET(BaseJFET):
    """Circuit symbol for a P-channel junction field effect transistor."""

    def _construct(self) -> None:  # type: ignore[override]
        super()._construct(draw_gate_line=False)

        height = config_eng.symbol.tripole_height
        # arrow pointing out of the channel
        arrow = mn.Arrow(
            start=0.5 * height * mn.UP,
            end=height * mn.UP,
            buff=0,
            stroke_width=self.stroke_width,
            fill_opacity=1.0,
            max_tip_length_to_length_ratio=0.5,
            max_stroke_width_to_length_ratio=10.0,
        )
        self._body.add(arrow)


class BaseMOSFET(Tripole):
    """Circuit symbol for a MOSFET with unspecified type."""

    def __init__(
        self,
        channel_type: Literal["enhancement", "depletion"] = "enhancement",
        **kwargs: Any,
    ) -> None:
        """Construct a basic MOSFET object.

        Parameters
        ----------
        channel_type : Literal['enhancement', 'depletion'], optional
            The type of MOSFET channel. Determines whether the transistor operates
            in enhancement or depletion mode. Defaults to "enhancement".
        **kwargs
            Additional keyword arguments passed to the parent class constructor.
        """
        width = config_eng.symbol.tripole_width
        height = config_eng.symbol.tripole_height
        # Add a bias to the top terminal
        biased_top = Terminal(
            position=np.array([-0.35 * width, height, 0.0]), direction=mn.UP
        )
        self.channel_type = channel_type
        super().__init__(None, None, biased_top, **kwargs)

    def _construct(self, draw_middle_line: bool = True) -> None:
        super()._construct()

        width = config_eng.symbol.tripole_width
        height = config_eng.symbol.tripole_height

        # lines from the gate
        line_gate = mn.VMobject()
        line_gate.start_new_path(np.array([-0.35 * width, height, 0.0]))
        line_gate.add_line_to(np.array([-0.35 * width, 0.65 * height, 0.0]))
        line_gate.add_line_to(np.array([0.35 * width, 0.65 * height, 0.0]))
        line_gate.match_style(self)
        self._body.add(line_gate)

        # horizontal line 2
        # (a single line for depletion type, 3 segments for enhancement type)
        if self.channel_type == "depletion":
            line_horizontal_2 = mn.Line(
                np.array([-0.42 * width, 0.5 * height, 0.0]),
                np.array([0.42 * width, 0.5 * height, 0.0]),
            ).match_style(self)
            self._body.add(line_horizontal_2)
        else:
            for x in [-0.3, 0.0, 0.3]:
                line_horizontal_2 = mn.Line(
                    np.array([(x - 0.12) * width, 0.5 * height, 0.0]),
                    np.array([(x + 0.12) * width, 0.5 * height, 0.0]),
                ).match_style(self)
                self._body.add(line_horizontal_2)

        # lines from the source
        line_source = mn.VMobject()
        line_source.start_new_path(0.5 * width * mn.LEFT)
        line_source.add_line_to(0.3 * width * mn.LEFT)
        line_source.add_line_to(np.array([-0.3 * width, 0.5 * height, 0.0]))
        line_source.match_style(self)
        self._body.add(line_source)

        # lines from the drain
        line_drain = mn.VMobject()
        line_drain.start_new_path(0.5 * width * mn.RIGHT)
        line_drain.add_line_to(0.3 * width * mn.RIGHT)
        line_drain.add_line_to(np.array([0.3 * width, 0.5 * height, 0.0]))
        line_drain.match_style(self)
        self._body.add(line_drain)

        # lines in the middle
        line_middle_1 = mn.Line(0.3 * width * mn.LEFT, mn.ORIGIN).match_style(self)
        self._body.add(line_middle_1)
        if draw_middle_line:
            line_middle_2 = mn.Line(mn.ORIGIN, 0.5 * height * mn.UP).match_style(self)
            self._body.add(line_middle_2)

    @property
    def gate(self) -> Terminal:
        """Return the gate terminal of the transistor."""
        return self.top

    @property
    def source(self) -> Terminal:
        """Return the source terminal of the transistor."""
        return self.left

    @property
    def drain(self) -> Terminal:
        """Return the drain terminal of the transistor."""
        return self.right


class NChannelMOSFET(BaseMOSFET):
    """Circuit symbol for an N-channel MOSFET."""

    def _construct(self) -> None:  # type: ignore[override]
        super()._construct(draw_middle_line=False)

        height = config_eng.symbol.tripole_height
        # arrow pointing into the channel
        arrow = mn.Arrow(
            start=mn.ORIGIN,
            end=0.5 * height * mn.UP,
            buff=0,
            stroke_width=self.stroke_width,
            fill_opacity=1.0,
            max_tip_length_to_length_ratio=0.5,
            max_stroke_width_to_length_ratio=10.0,
        )
        self._body.add(arrow)


class PChannelMOSFET(BaseMOSFET):
    """Circuit symbol for a P-channel MOSFET."""

    def _construct(self) -> None:  # type: ignore[override]
        super()._construct(draw_middle_line=False)

        height = config_eng.symbol.tripole_height
        # arrow pointing out of the channel
        arrow = mn.Arrow(
            start=0.5 * height * mn.UP,
            end=mn.ORIGIN,
            buff=0,
            stroke_width=self.stroke_width,
            fill_opacity=1.0,
            max_tip_length_to_length_ratio=0.5,
            max_stroke_width_to_length_ratio=10.0,
        )
        self._body.add(arrow)
