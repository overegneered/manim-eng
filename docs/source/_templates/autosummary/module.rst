{{ name | escape | underline }}

.. currentmodule:: {{ fullname }}

.. automodule:: {{ fullname }}

    {% if modules %}
    .. rubric:: Modules

    .. autosummary::
        :toctree: .
        :recursive:
    {% for module in modules %}
        {{ module }}
    {% endfor %}
    {% endif %}

    {% if classes %}
    .. rubric:: Classes

    .. autosummary::
        :toctree: .
        :nosignatures:
    {% for class in classes %}
        {{ class }}
    {% endfor %}
    {% endif %}

    {% if functions %}
    .. rubric:: Functions

    {% for function in functions %}
    .. autofunction:: {{ function }}
    {% endfor %}
    {% endif %}
