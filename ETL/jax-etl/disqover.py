from rdfwriter import Literal, Namespace, RDF, URIRef, RDFS
import urllib
import re

# you have to assign to these!
DISQ = Namespace("http://ns.ontoforce.com/2013/disqover#")
# global uri used as property for things that only need to be searchable but will be displayed in a different form.
toIndex = URIRef("http://ns.ontoforce.com/2013/disqover#toTextIndex")
synonym = URIRef("http://ns.ontoforce.com/2013/disqover#synonym")

NS = None
NST = None
# export functions


def rdf_str(st):
    return Literal(st)


def rdf_date(st):
    return Literal(st, datatype='date')


def to_uri(literal, conserveCase=False):
    literal = literal.strip()
    if not conserveCase:
        literal = literal.lower()
    return urllib.quote_plus(re.sub(r'[;,./ ]', '_', literal).encode("utf-8"))


def write_date(g, nctNode, name, date_str):
    if NS is None or NST is None:
        raise RuntimeError("disqover.NS/NST is not declared")
    if date_str:
        g.add((nctNode, NS[name], rdf_date(date_str)))
