from typing import Any

import manim as mn
from manim_eng._base.component import Component
from manim_eng._base.terminal import Terminal


class DummyComponent(Component):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        terminal_1 = Terminal(mn.RIGHT, mn.RIGHT)
        terminal_2 = Terminal(mn.LEFT, mn.LEFT)
        self.not_a_terminal = 3
        super().__init__([terminal_1, terminal_2], *args, **kwargs)

    def _construct(self) -> None:
        pass

    @property
    def terminal_1(self) -> Terminal:
        return self.terminals[0]

    @property
    def terminal_2(self) -> Terminal:
        return self.terminals[1]
