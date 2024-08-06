# manim-eng

manim-eng is a plugin for the [Manim Community](https://www.manim.community/) animation engine that introduces symbols and utilities for drawing engineering diagrams.
Currently this only includes circuits, but the goal is to extend this to structures in the future as well.

## Development

### Environment setup

manim-eng, like Manim itself, uses [Poetry](https://python-poetry.org/) as a build system. You will need Poetry
installed before proceeding. First, clone the repository with Git:

```shell
git clone https://github.com/overegneered/manim-eng.git
```

Then install dependencies with Poetry:

```shell
poetry install
```

Finally, install the pre-commit hooks:

```shell
pre-commit install
```

### Testing

manim-eng uses [pytest](https://pytest.org) as a testing framework. To run the test suite, you can use

```shell
poetry run pytest
```

though using an IDE integration, such as PyCharm's pytest runner, may be easier!
