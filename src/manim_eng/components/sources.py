"""Component symbols of sources."""

from manim_eng.components.base.modifiers import DiamondOuter, RoundOuter
from manim_eng.components.base.source import (
    ACSourceBase,
    DCSourceBase,
    EuropeanCurrentSourceBase,
    EuropeanVoltageSourceBase,
)

__all__ = [
    "ACSource",
    "ControlledACSource",
    "ControlledCurrentSource",
    "ControlledDCSource",
    "ControlledVoltageSource",
    "CurrentSource",
    "DCSource",
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


class DCSource(RoundOuter, DCSourceBase):
    """Circuit symbol for a US-style direct-current source."""

    def _construct(self) -> None:
        super()._construct()


class ControlledDCSource(DiamondOuter, DCSourceBase):
    """Circuit symbol for a US-style controlled direct-current source."""

    # TODO: The '+' and '-' on the symbol overlaps with the border. Fix it.

    def _construct(self) -> None:
        super()._construct()


class ACSource(RoundOuter, ACSourceBase):
    """Circuit symbol for a US-style alternating-current source."""

    def _construct(self) -> None:
        super()._construct()


class ControlledACSource(DiamondOuter, ACSourceBase):
    """Circuit symbol for a US-style controlled alternating-current source."""

    def _construct(self) -> None:
        super()._construct()
