How manim-eng works
===================

This is not going to be an explanation of how Manim works. Manim has its own
:external+manim:doc:`guide for that <guides/deep_dive>`. Rather, this is intended as a
narrative guide to the base classes that manim-eng adds to implement its basic
additional functionality.

The ``Mark`` class
------------------

The :class:`~.Mark` class is used for all of manim-eng's textual labels (i.e. labels,
annotations, current labels, and voltage labels), which are referred to by the umbrella
term *marks*. It is a thin wrapper around Manim's
:external+manim:class:`MathTex <manim.mobject.text.tex_mobject.MathTex>` object, which
adds a few new capabilities.

In particular, it allows the displayed mathematical text to be updated on the fly using
its :meth:`~.Mark.set` and :meth:`~.Mark.clear` methods, and implements functionality
for automatically positioning the mark relative two a set of two anchors. These both
have animation overrides to which other classes should delegate when animating changes
in marks.

Anchors
^^^^^^^

Marks hold references to two anchors: a ``centre_reference`` and an ``anchor``. Marks
are then positioned next to ``anchor`` on the opposite side to ``centre_reference``
using an updater.

Stealing a visualisation from :ref:`Marks remain upright <marks_remain_upright>` and
enabling :doc:`debug mode <debug_mode>`, we can see this graphically.

.. manim:: RotatingResistor
    :hide_source:

    from manim_eng import *

    config.frame_width = 2.5
    config.pixel_width = 512
    config.pixel_height = 512
    config_eng.debug = True

    class LinedSector(Sector):
        def __init__(self, **kwargs):
            super().__init__(**kwargs)
            self.add(Arc(
                radius=self.outer_radius,
                start_angle=self.start_angle,
                angle=self.angle,
                color=self.color,
            ))

    class CardinalSector(LinedSector):
        def __init__(self):
            super().__init__(
                radius=1,
                start_angle=-5 * DEGREES,
                angle=10 * DEGREES,
                color=BLUE,
                fill_color=BLUE,
                fill_opacity=0.3,
            )

    class SubCardinalSector(LinedSector):
        def __init__(self):
            super().__init__(
                radius=1,
                start_angle=5 * DEGREES,
                angle=80 * DEGREES,
                color=RED,
                fill_color=RED,
                fill_opacity=0.3,
            )

    class RotatingResistor(Scene):
        def construct(self):
            right = CardinalSector()
            ur = SubCardinalSector()
            up = CardinalSector().rotate(0.5 * PI, about_point=ORIGIN)
            ul = SubCardinalSector().rotate(0.5 * PI, about_point=ORIGIN)
            left = CardinalSector().rotate(PI, about_point=ORIGIN)
            dl = SubCardinalSector().rotate(PI, about_point=ORIGIN)
            down = CardinalSector().rotate(-0.5 * PI, about_point=ORIGIN)
            dr = SubCardinalSector().rotate(-0.5 * PI, about_point=ORIGIN)
            sectors = [up, ul, left, dl, down, dr, right, ur]

            self.add(*sectors)
            r = Resistor().set_label("R")
            self.add(r)

            dot = Dot(color=GREEN).shift(UP)
            self.add(dot)

            self.play(
                Rotating(r, run_time=10),
                Rotating(dot, run_time=10, about_point=ORIGIN),
            )

The purple centre anchor in the middle is the ``centre_reference`` and the red label
anchor is the ``anchor`` for the label mark with the text *R*. The *R* is kept with one
edge next to its ``anchor`` while staying opposite the ``centre_reference``. In
practice, this means that the *R* is kept in the most logical position to place it when
drawing a circuit symbol.

Anchors are implemented using the very simple :class:`~.Anchor` base class and
specialisations for each anchor type (see :mod:`~.anchor`). Their position is accessed
using the ``pos`` property.


The ``Markable`` class
----------------------

The :class:`~.Markable` class is the abstract base class of almost all manim-eng
mobjects. Its purpose is to add the functionality required to be able to attach marks to
mobjects and have them be rotationally invariant. To see what I mean by this, consider
the rotating resistor above, and note that the *R* does not rotate, despite being owned
by the resistor mobject.

To achieve this, each markable maintains two private
:external+manim:class:`VGroup <manim.mobject.types.vectorized_mobject.VGroup>`\ s:
``__marks`` and ``__rotate``. All rotation operations are then overloaded to apply just
to the ``__rotate`` group, and the standard operations of ``add()``, ``add_to_back()``,
and ``remove()`` are then overloaded to automatically sort marks into the ``__marks``
group and everything else into ``__rotate``.

There are also, of course, animation overrides for all added methods.
