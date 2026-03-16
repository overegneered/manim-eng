from typing import Any, cast
from unittest import mock

import manim as mn

from manim_eng.components.base.component import Component
from manim_eng.components.base.terminal import Terminal


class DummyComponent(Component):
    def __init__(self, **kwargs: Any) -> None:
        left = Terminal(mn.LEFT, mn.LEFT)
        right = Terminal(mn.RIGHT, mn.RIGHT)
        self.not_a_terminal = 3
        super().__init__([left, right], **kwargs)

    def _construct(self) -> None:
        pass

    @property
    def left(self) -> Terminal:
        return self.pins[0]

    @property
    def right(self) -> Terminal:
        return self.pins[1]


class DummyComponentMockedTerminals(Component):
    def __init__(self, **kwargs: Any) -> None:
        left = mock.MagicMock(Terminal)
        right = mock.MagicMock(Terminal)
        self.not_a_terminal = 3
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
    def cast_terminals(self) -> list[mock.MagicMock]:
        return cast(list[mock.MagicMock], self.pins)
