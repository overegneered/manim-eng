"""Component symbols of sources."""

from manim_eng.components.base.modifiers import DiamondOuter, RoundOuter
from manim_eng.components.base.source import (
    EuropeanCurrentSourceBase,
    EuropeanVoltageSourceBase,
)

__all__ = [
    "ControlledCurrentSource",
    "ControlledVoltageSource",
    "CurrentSource",
    "VoltageSource",
]


class VoltageSource(RoundOuter, EuropeanVoltageSourceBase):
    """Circuit symbol for a voltage source."""

    def _construct(self) -> None:
        super()._construct()


class ControlledVoltageSource(DiamondOuter, EuropeanVoltageSourceBase):
    """Circuit symbol for a controlled voltage source."""

    def _construct(self) -> None:
        super()._construct()


class CurrentSource(RoundOuter, EuropeanCurrentSourceBase):
    """Circuit symbol for a current source."""

    def _construct(self) -> None:
        super()._construct()


class ControlledCurrentSource(DiamondOuter, EuropeanCurrentSourceBase):
    """Circuit symbol for a controlled current source."""

    def _construct(self) -> None:
        super()._construct()
