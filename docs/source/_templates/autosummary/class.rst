{{ name | escape | underline }}

.. currentmodule:: {{ module }}

.. autoclass:: {{ name }}
    :members:
    :show-inheritance:

    {% if attributes %}
    .. rubric:: Attributes

    .. autosummary::
        :nosignatures:
        {% for attribute in attributes %}
        {{ name }}.{{ attribute }}
        {% endfor %}
    {% endif %}
