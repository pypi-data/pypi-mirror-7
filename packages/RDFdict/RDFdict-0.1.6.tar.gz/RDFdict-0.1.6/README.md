RDFdict
=======

A python class for a nested dictionaries representation of RDF quads and triples.

Simple usage:

    >>> from rdfdict import RDFdict
    >>> some_triples = ( ( 's1', 'p1', 'o1' ), ( 's2', 'p2', 'o2' ) )
    >>> my_rdfdict = RDFdict(triples=some_triples)
    >>> my_rdfdict.default_graph()
    {'s2': {'p2': 'o2'}, 's1': {'p1': 'o1'}}
    >>> list(my_rdfdict.graphs())
    [('DEFAULT', {'s2': {'p2': 'o2'}, 's1': {'p1': 'o1'}})]

RDFdict supports quads or triples.  Unless otherwise specified the default graph is called 'DEFAULT'.  When retrieving
multiple named graphs they are provided in a list of (name, graph_dictionary ) tuples.  When there are multiple objects
for a given subject and predicate, the predicate appears once and the objects appear in a list.

Although mainly intended for use with RDF and JSON, RDFdict is actually neutral to either.  It does not attempt to
manage conversions from RDF to JSON, but if you use RDFlib URIRefs and Literals as the elements in your graphs, they
will be correctly converted by json.dumps.  See test/test_withrdflib.py for examples.

