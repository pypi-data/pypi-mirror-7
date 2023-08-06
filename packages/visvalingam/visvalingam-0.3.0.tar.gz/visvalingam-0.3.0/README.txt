=================
Visvalingam-Wyatt
=================

Simple python implementation of a `famous algorithm`_ : the Visvalingam-Wyatt simplification.

.. _famous algorithm: https://hydra.hull.ac.uk/assets/hull:8343/content

Installation
------------

Using pip ::

    $ pip install visvalingam


You can download the source using ::

    git clone https://github.com/milkbread/Visvalingam-Wyatt.git

Examples execution
------------------

The whole example is located in the ``example/`` directory ::

    $ cd example

Script usage
~~~~~~~~~~~~

Dummy ::

	$ python simplify.py -i <inFile> -o <outFile> -t <tolerance>

Example ::

	python simplify.py -i in.json -o out.json -t 0.0005

Help ::

	python simplify.py -h

View results in browser
-----------------------

This is an exemplary workflow for tests :

- Download the repository
- Simplify your data ::

    python simplify.py -i in.json -o out.json -t 0.0005

- setup local server (**necessary for D3.js**) ::

    python -m SimpleHTTPServer 8888

- open in browser: http://localhost:8888/index.html
- *If needed* adjust the filenames within the ``example/index.html`` (lines 24 & 28)
- evaluate the resulting data and try another threshold

**Impatient to see some results?** See the `example/index.html`_ here!

.. _example/index.html: http://milkbread.github.io/Visvalingam-Wyatt

Inspired by M.Bostocks JavaScript-Implementation:
-------------------------------------------------

- Explanation_
- Code_

.. _Explanation: http://bost.ocks.org/mike/simplify/)
.. _Code: http://bost.ocks.org/mike/simplify/simplify.js)


.. vim: ft=rst
