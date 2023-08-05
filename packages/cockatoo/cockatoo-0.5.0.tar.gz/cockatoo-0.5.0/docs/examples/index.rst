Examples
========
.. highlight:: bash

cockatoo command line
----------------------

cockatoo comes with a command line utility for computing distances. To get a
list of commands run::

  $ cockatoo --help
  Usage: cockatoo [OPTIONS] COMMAND [ARGS]...

  Options:
    -v, --verbose  Turn on verbose logging
    --help         Show this message and exit.

  Commands:
    cdist    Compute the distance between 2 cocktails
    convert  Convert CSV screen to JSON format
    hclust   Perform hierarchical clustering on a screen
    isim     Compute the internal similarity score for a...
    sdist    Compute the distance between 2 screens
    version  Print cockatoo version

To get help for a specific command run::

  $ cockatoo sdist --help
  Usage: cockatoo sdist [OPTIONS]

    Compute the distance between 2 screens

  Options:
    -1, --screen1 PATH     Path to screen1 in JSON format  [required]
    -2, --screen2 PATH     Path to screen2 in JSON format  [required]
    -w, --weights WEIGHTS  weights=1,1
    --help                 Show this message and exit.

Compute distance between cocktails
+++++++++++++++++++++++++++++++++++

Create two JSON files (ck1.json, ck1.json) describing your cocktails. See
:doc:`../tutorial` for file format specification. Then run::

  $ cockatoo cdist -1 ck1.json -2 ck1.json

Compute distance between screens
+++++++++++++++++++++++++++++++++++

Create two JSON files (s1.json, s2.json) describing your screens. See
:doc:`../tutorial` for file format specification. Then run::

  $ cockatoo sdist -1 s1.json -2 s2.json

Convert CSV screen to JSON
+++++++++++++++++++++++++++

Converting a screen stored in CSV format to JSON requires your CSV file to be in
a specific format, see the :doc:`../tutorial` for more info. You will also need
a compound summary file which includes data on each compound found in your
cocktails. See the data/hwi-compounds.csv file for an example. To convert the
screen run::

  $ cockatoo convert -i screen.csv -o screen.json -n screen_name -s hwi-compounds.csv

Compute interal similarity
+++++++++++++++++++++++++++

This command will compute the interal similarity score for a given screen.
Create a JSON file (s1.json) describing your screen. See :doc:`../tutorial` for
file format specification. Then run::

  $ cockatoo isim -s s1.json

Hierarchical clustering
+++++++++++++++++++++++++++

This command will perform hierarchical clustering on a given screen. This
command requires python modules: `numpy <http://www.numpy.org/>`_, `scipy
<http://www.scipy.org/>`_, and `matplotlib <http://matplotlib.org/>`_ to be
installed.  Create a JSON file (s1.json) describing your screen. See
:doc:`../tutorial` for file format specification. Then run::

  $ cockatoo -v hclust -s s1.json -p -d -n

cockatoo API
----------------------

An example of using cockatoo python API:

.. code-block:: python

  import cockatoo

  ck1 = cockatoo.screen.parse_cocktail('ck1.json')
  ck2 = cockatoo.screen.parse_cocktail('ck2.json')
  dist = cockatoo.metric.distance(ck1, ck2)
  print "Distance: {}".format(dist)

