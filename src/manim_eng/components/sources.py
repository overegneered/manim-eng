"""Sources."""

from manim_eng.components.base.source import (
    DiamondOuter,
    EuropeanCurrentSourceBase,
    EuropeanVoltageSourceBase,
    RoundOuter,
)


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
