# manim-eng

manim-eng is a plugin for the [Manim Community](https://www.manim.community/) animation engine that introduces symbols and utilities for drawing engineering diagrams.
Currently this only includes circuits, but the goal is to extend this to structures in the future as well.

## Setting up a development environment

manim-eng, like Manim itself, uses [Poetry](https://python-poetry.org/) as a build system. You will need Poetry
installed before proceeding. First, clone the repository:

```shell
git clone https://github.com/overegneered/manim-eng.git
```

Then install dependencies with Poetry:

```shell
poetry install
```

Finally, install the pre-commit hooks with

```shell
pre-commit install
```
