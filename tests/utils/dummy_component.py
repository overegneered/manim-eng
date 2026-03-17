from typing import Any, cast
from unittest import mock

import manim as mn

from manim_eng.components.base.component import Component
from manim_eng.components.base.pin import Pin


class DummyComponent(Component):
    def __init__(self, **kwargs: Any) -> None:
        left = Pin(mn.LEFT, mn.LEFT)
        right = Pin(mn.RIGHT, mn.RIGHT)
        self.not_a_pin = 3
        super().__init__([left, right], **kwargs)

    def _construct(self) -> None:
        pass

    @property
    def left(self) -> Pin:
        return self.pins[0]

    @property
    def right(self) -> Pin:
        return self.pins[1]


class DummyComponentMockedPins(Component):
    def __init__(self, **kwargs: Any) -> None:
        left = mock.MagicMock(Pin)
        right = mock.MagicMock(Pin)
        self.not_a_pin = 3
        super().__init__([left, right], **kwargs)

    def _construct(self) -> None:
        pass

    @property
    def left(self) -> mock.MagicMock:
        return cast(mock.MagicMock, self.pins[0])

    @property
    def right(self) -> mock.MagicMock:
        return cast(mock.MagicMock, self.pins[1])

    @property
    def cast_pins(self) -> list[mock.MagicMock]:
        return cast(list[mock.MagicMock], self.pins)
