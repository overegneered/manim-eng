import manim as mn
import manim.typing as mnt
from utils.pin_mocked import PinMockedParent

from manim_eng import ManualWire


def manual_wire_from_vertices(vertices: list[mnt.Point3D]) -> ManualWire:
    """Create a ManualWire whose ``get_all_vertices()`` equals ``vertices``.

    The first and last entries in ``vertices`` become ``start.base`` and
    ``end.base`` respectively. Everything in between becomes the list of
    explicit corner points passed to ``ManualWire``.
    """
    start = PinMockedParent(vertices[0], mn.RIGHT)
    end = PinMockedParent(vertices[-1], mn.RIGHT)
    return ManualWire(start, end, vertices[1:-1])
