import os
from unittest import mock

import pytest
from manim_eng.components.base import Terminal
from manim_eng.components.base.component import Component

from .test_utils.dummy_component import DummyComponent, DummyComponentMockedTerminals

# Create the media directory required by some of the tests if it doesn't already exist
# Ordinarily Manim would create this, but the tests run Manim code outside the usual
# framework (i.e. not within a Scene's construct() method), so we have to do some work
# ourselves.
os.makedirs("media", exist_ok=True)


@pytest.fixture()
def dummy_component() -> Component:
    return DummyComponent()


@pytest.fixture()
def dummy_component_mocked_terminals() -> Component:
    dummy_component = DummyComponentMockedTerminals()
    dummy_component.terminals[0] = mock.MagicMock(Terminal)
    dummy_component.terminals[1] = mock.MagicMock(Terminal)
    return dummy_component
