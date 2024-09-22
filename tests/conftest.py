import os

import pytest
from manim_eng._base.component import Component

from .test_utils.dummy_component import DummyComponent

# Create the media directory required by some of the tests if it doesn't already exist
# Ordinarily Manim would create this, but the tests run Manim code outside the usual
# framework (i.e. not within a Scene's construct() method), so we have to do some work
# ourselves.
os.makedirs("media", exist_ok=True)


@pytest.fixture()
def dummy_component() -> Component:
    return DummyComponent()
