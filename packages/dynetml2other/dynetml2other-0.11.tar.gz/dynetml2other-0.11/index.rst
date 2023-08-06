.. dynetml2other documentation master file, created by
   sphinx-quickstart on Thu Jun 12 16:17:14 2014.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Import DyNetML_ into Python_, NetworkX_, and igraph_
====================================================

dynetml2other provides an importer and a set of wrapper classes for DyNetML files that allow them to be
used with several Python graph libraries. These wrapper classes also support exporting data in DyNetML format, meaning
that it can be created, used with this package, and then save out for analysis with other tools.

The current way to use the module is by giving the dynetml2other method the path to the file you
want to parse::

    >>> from dynetml2other import dynetml2other
    >>> dmn_with_graphs_as_networkx = dynetml2other('path_to_dynamic_metanetwork_from_twitter.xml', 'networkx')
    >>> dmn_with_graphs_as_igraphs = dynetml2other('path_to_dynamic_metanetwork_from_twitter.xml', 'igraph')
    >>> dmn_with_graphs_as_dicts = dynetml2other('path_to_dynamic_metanetwork_from_twitter.xml')
    >>> dmn_with_graphs_as_dicts
    <dynetml2other.DynamicMetaNetwork.DynamicMetaNetwork instance at 0x10e857950>
    >>> mn_with_graphs_as_dicts = dynetml2other('vanilla_metanetwork_for_some_project.xml')
    >>> mn_with_graphs_as_dicts
    <dynetml2other.MetaNetwork.MetaNetwork instance at 0x10e857098>
    >>> dmn_with_graphs_as_dicts.attributes
    {'id': 'Twitter JSON - 1 Hour'}
    >>> dmn_with_graphs_as_dicts[0]
    <dynetml2other.MetaNetwork.MetaNetwork instance at 0x10e857cb0>
    >>> len(dmn_with_graphs_as_dicts.metanetworks
    23
    >>> dmn_with_graphs_as_dicts.metanetworks[0].attributes
    {'date': '20130503T10:00:00', 'id': '2013-05-03 10 AM'}
    >>> dmn_with_graphs_as_dicts.metanetworks[0].propertyIdentities
    {'importFile': ('text', False), 'importLastTweetDate': ('date', False), 'lastTweetDate': ('dat
    e', False), 'importAggregationPeriod': ('text', False), 'importFirstTweetDate': ('date', False
    ), 'firstTweetDate': ('date', False), 'importFileFormat': ('text', False)}
    >>> dmn_with_graphs_as_dicts.write_dynetml('a_copy_of_the_dynetml.xml')

To define the method properly:


.. automodule:: dynetml2other
   :members: main


If the file contains a meta-network, and based on t will be parsed into an instance of :doc:`/MetaNetwork`, which stores graph data in dictionaries, or into one of its SubClasses:
 * :doc:`MetaNetworkNX </MetaNetworkNetworkX>`, which stores graph data in networkx.Graphs_ and networkx.DiGraphs_
 * :doc:`MetaNetworkIG </MetaNetworkIGraph>`, which stores graph data in igraph.Graphs_


If the file contains a dynamic meta-network, it will be parsed into a instance of :doc:`/DynamicMetaNetwork`, which
contains a list of MetaNetworks or of one of MetaNetwork's SubClasses. Types of MetaNetworks cannot be mixed within a
DynamicMetaNetwor.


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