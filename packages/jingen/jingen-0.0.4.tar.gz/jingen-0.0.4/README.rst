Jingen
======

Jingen generates files from Jinja2 based template files.

Usage:
~~~~~~

Assuming a vars file mock\_vars.py

.. code:: python

    VARS = {
        "test_var": "vars_file_test_value"
    }

and a template file: mock.template:

.. code:: text

    I'M A MOCK TEMPLATE AND MY VAR IS: {{ test_var }}

.. code:: python

    from jingen.jingen import Jingen

    template_file = "mock.template"
    vars_source = "tests/resources/mock_vars.py"  # alternatively, can be a dict
    output_file = "tests/resources/manual_test_result.file"
    templates_dir = "tests/resources/"
    make_file = True
    verbose = True

    i = Jingen(
        template_file=template_file,
        vars_source=vars_source,
        output_file=output_file,
        templates_dir=templates_dir,
        make_file=make_file,
        verbose=verbose)
    output = i.generate()

    print output
    ...
    I'M A MOCK TEMPLATE AND MY VAR IS: vars_file_test_value

Output would be:

.. code:: text

    ### DEBUG - generating template from tests/resources//mock.template
    ### DEBUG - creating file: tests/resources/manual_test_result.file with content:
    I'M A MOCK TEMPLATE AND MY VAR IS: vars_file_test_value
