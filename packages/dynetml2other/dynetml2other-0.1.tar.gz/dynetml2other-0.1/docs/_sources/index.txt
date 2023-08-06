.. dynetml2other documentation master file, created by
   sphinx-quickstart on Thu Jun 12 16:17:14 2014.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Import DyNetML_ into Python_, NetworkX_, and igraph_
====================================================

dynetml2other provides an importer and a set of wrapper classes for DyNetML files that allow them to be
used with several Python graph libraries. Thes wrapper classes also support exporting data in DyNetML format, meaning
that it can be created, used with this package, and then save out for analysis with other tools.


The principle helper class is the dynetml2other method:

.. automodule:: dynetml2other
   :members: main


If the file contains a meta-network, it will be parsed into an instance of :doc:`/MetaNetwork`, which stores graph data
in dictionaries, or into one of its SubClasses:
 * :doc:`MetaNetworkNX </MetaNetworkNetworkX>`, which stores graph data in networkx.Graphs_ and networkx.DiGraphs_
 * :doc:`MetaNetworkIG </MetaNetworkIGraph>`, which stores graph data in igraph.Graphs_

:doc:`/MetaNetwork` itself contains no graph data, so if you use the base instance you will lose any graph edges.

If the file contains a dynamic meta-network, it will be parsed into a instance of :doc:`/DynamicMetaNetwork`, which
contains a list of one of the MetaNetwork SubClasses.


Contents
========

.. toctree::
   :maxdepth: 2

   /DynamicMetaNetwork
   /MetaNetwork
   /MetaNetworkNetworkX
   /MetaNetworkIGraph
   /dynetmlparsingutils


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`


.. _DyNetML: http://www.casos.cs.cmu.edu/projects/dynetml/
.. _Python: http://www.python.org
.. _igraph: http://igraph.org/python/
.. _NetworkX: http://networkx.github.io
.. _NetworkX.Graphs: http://networkx.github.io/documentation/latest/reference/classes.graph.html#networkx.Graph
.. _NetworkX.DiGraphs: http://networkx.github.io/documentation/latest/reference/classes.digraph.html#networkx.DiGraph
.. _igraph.Graphs: http://igraph.org/python/doc/igraph.Graph-class.html