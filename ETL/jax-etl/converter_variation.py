import json
import logging
import os
import sys
import urllib

from rdfwriter import *
import disqover

logging.basicConfig(level=logging.INFO, stream=sys.stdout)
logger = logging.getLogger()

JV = Namespace("http://vocab.jax.org/", 'JV')
JD = Namespace("http://data.jax.org/", 'JD')
SKOS = Namespace("http://www.w3.org/2004/02/skos/core#", 'SKOS')
XSD = Namespace("http://www.w3.org/2001/XMLSchema#", 'XSD')
SCHEMA = Namespace("http://schema.org/", 'schema')
RDFS = Namespace("http://www.w3.org/2000/01/rdf-schema#", 'rdfs')

class Assay(object):

    def write_ttl(self, data, g):

        passage_uri = URIRef("http://data.jax.org/passage/" + disqover.to_uri(data['sample']))
        g.add((passage_uri, RDF.type, JV['Passage']))
        g.add((passage_uri, JV['hasPassage'], Literal(data['passage num'])))
        g.add((passage_uri, RDFS['label'], Literal(data['sample'])))

        mutation_uri = None
        mutation_id = data['rs variants'].split(';')
        for mut in mutation_id:
            if mut[0:2] == "rs":
                mutation_uri = URIRef("http://identifiers.org/dbsnp/" + disqover.to_uri(mut))

        model_id = ''
        if len(data['model id']) == 2:
            model_id = 'TM000'+ data['model id']
        elif len(data['model id']) == 3:
            model_id = 'TM00'+ data['model id']
        elif len(data['model id']) == 4:
            model_id = 'TM0'+ data['model id']
        elif len(data['model id']) == 5:
            model_id = 'TM'+ data['model id']
        tumor_uri = URIRef("http://data.jax.org/tumor/" + model_id)
        g.add((tumor_uri, RDF.type, JV['Tumor']))
        g.add((tumor_uri, RDFS['label'], Literal(model_id)))
        g.add((tumor_uri, JV['hasPassage'], passage_uri))


        if mutation_uri:
            g.add((mutation_uri, RDF.type, JV['Mutation']))
            g.add((mutation_uri, RDFS['label'], Literal(mut)))
            g.add((tumor_uri, JV['hasMutation'], mutation_uri))
            if data['chromosome']:
                g.add((mutation_uri, JV['hasChromosome'], Literal(data['chromosome'])))
            if data['consequence']:
                g.add((mutation_uri, JV['hasConsequence'], Literal(data['consequence'])))
            if data['seq position']:
                g.add((mutation_uri, JV['hasPosition'], Literal(data['seq position'])))
            if data['ref allele']:
                g.add((mutation_uri, JV['hasRefAllele'], Literal(data['ref allele'])))
            if data['alt allele']:
                g.add((mutation_uri, JV['hasAltAllele'], Literal(data['alt allele'])))
            if data['amino acid change']:
                g.add((mutation_uri, JV['hasAminoAcidChange'], Literal(data['amino acid change'])))
            if data['allele frequency']:
                g.add((mutation_uri, JV['hasAlleFrequence'], Literal(data['allele frequency'])))

            if data['gene id']:
                gene_uri = URIRef("http://identifiers.org/hgnc.symbol/" + disqover.to_uri(data['gene id']))
                g.add((mutation_uri, JV['hasGene'], gene_uri))

            assay_uri = URIRef("http://data.jax.org/tumor/" + disqover.to_uri(data['sample'] + '_' + model_id))
            g.add((assay_uri, RDF.type, JV['Assay']))
            g.add((assay_uri, RDFS['label'], Literal(data['sample'] + '_' + model_id)))
            g.add((assay_uri, JV['hasAssay'], assay_uri))
            g.add((passage_uri, JV['hasPassage'], assay_uri))
            g.add((tumor_uri, JV['hasMutation'], mutation_uri))
            g.add((assay_uri, JV['hasReadDepth'], Literal(data['read depth'])))
            g.add((assay_uri, JV['hasPlatform'], Literal(data['platform'])))


def main():

    outdir = sys.argv[1]
    data_file = sys.argv[2]

    filename = os.path.basename(os.path.splitext(data_file)[0])
    ttl_loc = os.path.join(outdir, filename)
    ttl = open(ttl_loc + "jax_variations.ttl", 'w')

    g = Graph(ttl)
    g.add(JV)
    g.add(JD)
    g.add(XSD)
    g.add(SKOS)
    g.add(SCHEMA)
    g.add(RDFS)

    with open(data_file, 'r') as data:
        data_json = json.load(data)
    for datapoint in data_json[0]['variation']:
        assay = Assay()
        assay.write_ttl(datapoint, g)

    g.serialize()

if __name__ == "__main__":
    main()
