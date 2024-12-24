# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "manim-eng"
copyright = "2024, overegneered"
author = "overegneered"
release = "0.1.0"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.duration",
    "sphinx.ext.doctest",
    "sphinx.ext.intersphinx",
    "sphinx.ext.napoleon",
    "manim.utils.docbuild.manim_directive",
]

templates_path = ["_templates"]
exclude_patterns = []  # type: ignore[var-annotated]
intersphinx_mapping = {
    "manim": ("https://docs.manim.community/en/stable", None)
}

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_static_path = ["_static"]
html_theme = "furo"
html_theme_options = {
    "dark_logo": "logo_no_text.png",
    "light_logo": "logo_light_no_text.png",
}
html_title = f"{project} {release}"
