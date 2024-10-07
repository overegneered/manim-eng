from typing import Any, cast
from unittest import mock

import manim as mn
from manim_eng.components.base.component import Component
from manim_eng.components.base.terminal import Terminal


class DummyComponent(Component):
    def __init__(self, **kwargs: Any) -> None:
        terminal_1 = Terminal(mn.RIGHT, mn.RIGHT)
        terminal_2 = Terminal(mn.LEFT, mn.LEFT)
        self.not_a_terminal = 3
        super().__init__([terminal_1, terminal_2], **kwargs)

    def _construct(self) -> None:
        pass

    @property
    def terminal_1(self) -> Terminal:
        return self.terminals[0]

    @property
    def terminal_2(self) -> Terminal:
        return self.terminals[1]


class DummyComponentMockedTerminals(Component):
    def __init__(self, **kwargs: Any) -> None:
        terminal_1 = mock.MagicMock(Terminal)
        terminal_2 = mock.MagicMock(Terminal)
        self.not_a_terminal = 3
        super().__init__([terminal_1, terminal_2], **kwargs)

    def _construct(self) -> None:
        pass

    @property
    def terminal_1(self) -> mock.MagicMock:
        return cast(mock.MagicMock, self.terminals[0])

    @property
    def terminal_2(self) -> mock.MagicMock:
        return cast(mock.MagicMock, self.terminals[1])

    @property
    def cast_terminals(self) -> list[mock.MagicMock]:
        return cast(list[mock.MagicMock], self.terminals)
