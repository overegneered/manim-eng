Extending manim-eng
===================

manim-eng was designed to be extensible, and these pages serve as a guide to its
'secret' public API of implementation classes. I say secret as these classes are not
imported by default; their imports are contained in an ``implementation`` submodule. To
get access, add the following to your file.

.. code-block:: python

    from manim_eng.implementation import *

.. toctree::
    :caption: Contents

    how_manim-eng_works
    debug_mode
    units
