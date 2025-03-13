The debug mode
==============

Debug mode is quite handy for debugging component symbols. It displays the anchors of
:class:`~.Markable`\ s in as coloured rings according to the following: [#anchorcolours]_

=============  ======
Anchor type    Colour
=============  ======
Centre         Purple
Label          Red
Annotation     Blue
Terminal end   Green
Current label  Orange
Voltage label  Yellow
=============  ======

As a visual example, here is a resistor with a current and voltage arrow when rendered
in debug mode.

.. manim:: DebugExample
    :hide_source:
    :save_last_frame:

    from manim_eng import *

    config.frame_width = 2.5
    config.pixel_width = 512
    config.pixel_height = 512
    config_eng.debug = True

    class DebugExample(Scene):
            def construct(self):
                r = Resistor(
                    label="R",
                    annotation=10 * KILO*OHM,
                ).set_current("i").shift(0.25 * DOWN)
                self.add(r)
                self.add(r.voltage("right", "left", "V"))

.. note::

    As terminals and voltage arrows are also :class:`~.Markable` instances, they also
    have purple centre anchors!

Activating the debug mode
-------------------------

To activate debug mode, set the ``debug`` configuration option to ``True``:

.. code-block:: python

    config_eng.debug = True
    # your code here...

or

.. code-block:: python

    with tempconfig_eng({"debug": True}):
        # your code here...

are your best in-code bets, though you can always use config files as well. See the
:doc:`configuration guide <../guides/configuration>` for more details on the
configuration system.

.. rubric:: Footnotes

.. [#anchorcolours] Anchor colours can be configured using the ``anchor`` subconfig
    table. See :class:`~.ManimEngConfig` for the overall config and
    :class:`~.AnchorDisplayConfig` for anchor-specific config, as well as the
    :doc:`guide on configuration <../guides/configuration>`.
