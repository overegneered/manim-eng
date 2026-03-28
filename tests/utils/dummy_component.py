from typing import Any, cast
from unittest import mock

import manim as mn
import numpy as np

from manim_eng.components.base.component import Component
from manim_eng.components.base.pin import Pin


class DummyComponent(Component):
    def __init__(self, **kwargs: Any) -> None:
        left = Pin(mn.LEFT, mn.LEFT, parent=self)
        right = Pin(mn.RIGHT, mn.RIGHT, parent=self)
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


class DummyComponentOffCentre(Component):
    """DummyComponent whose logical centre is offset from the geometric centre.

    The ``_centre_anchor`` is shifted to ``[0.3, 0.2, 0.0]`` after construction,
    making the logical centre distinct from the geometric centre in both axes.
    This is needed for tests that assert snap behaviour is non-trivial.
    """

    def __init__(self, **kwargs: Any) -> None:
        left = Pin(mn.LEFT, mn.LEFT, parent=self)
        right = Pin(mn.RIGHT, mn.RIGHT, parent=self)
        self.not_a_pin = 3
        super().__init__([left, right], **kwargs)
        # _centre_anchor is created inside Component.__init__(), so the shift
        # must happen after super().__init__() returns.
        self._centre_anchor.move_to(np.array([0.3, 0.2, 0.0]))

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
