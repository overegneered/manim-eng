from typing import Any
from unittest import mock

import manim as mn
import manim.typing as mnt

from manim_eng.components.base.component import Component
from manim_eng.components.base.pin import Pin


class PinMockedParent(Pin):
    """Pin that mocks its parent to simplify testing setups."""

    def __init__(
        self, position: mnt.Point3D, direction: mnt.Vector3D, *args: Any, **kwargs: Any
    ) -> None:
        super().__init__(
            position,
            direction,
            mock.MagicMock(Component),
            *args,
            **kwargs,
        )


class PinTipOnly(PinMockedParent):
    """Minimal pin stub that exposes only the ``tip`` attribute."""

    def __init__(self, tip: mnt.Point3D) -> None:
        super().__init__(tip - mn.RIGHT, mn.RIGHT, length=1.0)
