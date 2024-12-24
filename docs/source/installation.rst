Installation
============

First of all, you'll need to install Manim itself — check out the
:external+manim:doc:`installation guide <installation>` in the Manim docs for that.
Then, simply

.. code-block:: shell

    pip install manim-eng

if you're using pip, or use your package manager — if you were using Poetry for
instance, you'd do the following.

.. code-block:: shell

    poetry add manim-eng


Usage
-----

Set up your project however you please (see
:external+manim:doc:`Manim's guide <tutorials/quickstart>` if you're unsure), and then simply
add

.. code-block:: python

    from manim_eng import *


to the top of your file. This brings all of manim-eng's
:external:class:`Mobjects <manim.mobject.mobject.Mobject>` into scope. That's it!
