.. _cli:

Command line Interface
**********************

You can call your script in command line to dynamically modify importation params.

To prevent from importing csv file headers, type the following::

    $ ./your_script.py -o1

To import only few lines (First ten's), type the following::

    $ ./your_script.py -l10

For further details::
    
    $ ./your_script --help

.. note::

    Command line options have a higher priority than the class definition arguments.
    For example, the configuration of your
    :class:`Odoo <csv2odoo.models.connector.Odoo>` instance will be overwritten
    by the command line options you specified. Same for
    :class:`Session <csv2odoo.models.session.Session>` session arguments.

Shell options
-------------

Usage: SCRIPT NAME [options]

Options:
  -h, --help            show this help message and exit
  -f FILENAME, --filename=FILENAME
                        The CSV file to import.
  -s DELIMITER, --separator=DELIMITER
                        The delimiter of the CSV file.
  -g QUOTECHAR, --quotechar=QUOTECHAR
                        The quotechar of the CSV file.
  -e ENCODING, --encoding=ENCODING
                        The encoding of the CSV file.
  -o OFFSET, --offset=OFFSET
                        Offset (Usually used for header omission, default=1)
  -d, --debug           debug mode
  -v, --verbose         verbose mode
  -q, --quiet           don't print anything to stdout
  -l LIMIT, --limit=LIMIT
                        Limit
  -u USERNAME, --username=USERNAME
                        Username
  -p PASSWORD, --password=PASSWORD
                        Password
  -r HOST, --host=HOST  Host to contact
  -t PORT, --port=PORT  Port used
  -b DBNAME, --database=DBNAME
                        Database name

Script automation
-----------------

To help you to configure your first script, a script automation has been added.
In order to properly configure each binding for each `csv` files, you can call
the module :class:`Tool <csv2odoo.tools>` with `python -m` option.

.. code-block:: console

    $ python -m csv2odoo.tools /path/to/your/csv/file.csv > my_script.py

This will result of a preconfigured script for the file specified. If you have
more than one file, you can juste add a list of paths separated by coma.

.. code-block:: console

    $ python -m csv2odoo.tools /path/to/your/csv/file_#1.csv,/path/to/your/csv/file_#2.csv > my_script.py

.. note::

    Internaly, it is the :class:`csv.Sniffer` class which is used to detect dialect.

.. seealso::

    :func:`generate_code <csv2odoo.tools.generate_code>`
