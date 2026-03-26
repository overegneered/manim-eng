"""Component symbols of operational amplifiers."""

from typing import Any, cast

import manim as mn
import numpy as np

from manim_eng import config_eng
from manim_eng.components.base.component import Component
from manim_eng.components.base.terminal import Terminal


class OpAmp(Component):
    """Circuit symbol of operational amplifiers (Op-Amps).

    Operational Amplifier (Op-Amp) is a high gain voltage amplifier with 5 terminals:
    V+, V-, Vout, Vdd, and Vss.

    By default, only V+, V-, and Vout pins are created. Vdd and Vss can be added by
    accessing the component's ``vdd`` and ``vss`` properties.
    """

    def __init__(self, **kwargs: Any) -> None:
        half_width = config_eng.symbol.opamp_width * 0.5
        half_spacing = config_eng.symbol.terminal_spacing * 0.5
        terminal_vp = Terminal(
            position=half_width * mn.LEFT + half_spacing * mn.UP, direction=mn.LEFT
        )
        terminal_vn = Terminal(
            position=half_width * mn.LEFT + half_spacing * mn.DOWN, direction=mn.LEFT
        )
        terminal_vout = Terminal(position=half_width * mn.RIGHT, direction=mn.RIGHT)
        terminals = [terminal_vp, terminal_vn, terminal_vout]
        super().__init__(terminals, **kwargs)

        self._terminal_vdd: Terminal | None = None
        self._terminal_vss: Terminal | None = None

        self.add_updater(self.__label_anchor_updater)
        self.add_updater(self.__annotation_anchor_update)
        self.update()

    def _construct(self) -> None:
        super()._construct()
        half_width = config_eng.symbol.opamp_width * 0.5
        half_height = config_eng.symbol.opamp_height * 0.5
        triangle = mn.Polygon(
            np.array([-half_width, half_height, 0.0]),
            np.array([-half_width, -half_height, 0.0]),
            np.array([half_width, 0.0, 0.0]),
        ).match_style(self)
        name1 = (
            mn.Text("+", font_size=config_eng.symbol.terminal_name_font_size)
            .match_style(self)
            .next_to(self.vp, mn.RIGHT, buff=config_eng.symbol.terminal_name_buff)
        )
        name2 = (
            mn.Text("-", font_size=config_eng.symbol.terminal_name_font_size)
            .match_style(self)
            .next_to(self.vn, mn.RIGHT, buff=config_eng.symbol.terminal_name_buff)
        )
        self._body.add(triangle, name1, name2)

    @property
    def vp(self) -> Terminal:
        """Return the V+ terminal."""
        return self.terminals[0]

    @property
    def vn(self) -> Terminal:
        """Return the V- terminal."""
        return self.terminals[1]

    @property
    def vout(self) -> Terminal:
        """Return the Vout terminal."""
        return self.terminals[2]

    @property
    def vdd(self) -> Terminal:
        """Return the Vdd terminal. Create the terminal if it does not exist."""
        if self._terminal_vdd is not None:
            return self._terminal_vdd
        # The terminal does not exist. Create it.
        quarter_height = config_eng.symbol.opamp_height * 0.25
        # * Do not use autovisibility for VDD and VSS pins, or otherwise creating
        # a model of 5-pin op-amp will be painful.
        vdd = Terminal(
            position=self.get_center() + quarter_height * mn.UP, direction=mn.UP
        )
        self.terminals.append(vdd)
        self._terminal_vdd = vdd
        self.update()
        return vdd

    @property
    def vss(self) -> Terminal:
        """Return the Vss terminal. Create the terminal if it does not exist."""
        if self._terminal_vss is not None:
            return self._terminal_vss
        # The terminal does not exist. Create it.
        quarter_height = config_eng.symbol.opamp_height * 0.25
        vss = Terminal(
            position=self.get_center() + quarter_height * mn.DOWN, direction=mn.DOWN
        )
        self.terminals.append(vss)
        self._terminal_vss = vss
        self.update()
        return vss

    def _reposition_label_anchor(self) -> None:
        """Reposition the label anchor to the right of `vdd` terminal.

        Only executes when `vdd` terminal, the label, and the label anchor exist.
        """
        if (
            self._terminal_vdd is not None
            and hasattr(self, "_label")
            and hasattr(self, "_label_anchor")
        ):
            up = self._terminal_vdd.direction
            right = self.vout.direction
            buff = 0.1
            self._label_anchor.next_to(self._terminal_vdd, right, buff=buff)
            self._label_anchor.shift(-up * buff)
            self._label.update()

    def _reposition_annotation_anchor(self) -> None:
        """Reposition the annotation anchor to the right of `vss` terminal.

        Only executes when `vss` terminal, the label, and the label anchor exists.
        """
        if (
            self._terminal_vss is not None
            and hasattr(self, "_annotation")
            and hasattr(self, "_annotation_anchor")
        ):
            down = self._terminal_vss.direction
            right = self.vout.direction
            buff = 0.1
            self._annotation_anchor.next_to(self._terminal_vss, right, buff=buff)
            self._annotation_anchor.shift(-down * buff)
            self._annotation.update()

    @staticmethod
    def __label_anchor_updater(mobject: mn.Mobject) -> None:
        """Update label position based on terminal positions."""
        opamp = cast(OpAmp, mobject)
        opamp._reposition_label_anchor()

    @staticmethod
    def __annotation_anchor_update(mobject: mn.Mobject) -> None:
        """Update annotation position based on terminal positions."""
        opamp = cast(OpAmp, mobject)
        opamp._reposition_annotation_anchor()
