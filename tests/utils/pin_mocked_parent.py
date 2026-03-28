from typing import Any
from unittest import mock

import manim.typing as mnt

from manim_eng.components.base.component import Component
from manim_eng.components.base.pin import Pin


class PinMockedParent(Pin):
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
