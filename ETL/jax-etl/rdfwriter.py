class URIRef(object):

    def __init__(self, uri):
        self.uri = uri

    def __str__(self):
        return "<{}>".format(self.uri)


class _BNodeBasic(object):
    counter = 0

    def __init__(self, node, predicateword):
        if not isinstance(node, URIRef):
            raise RuntimeError("1st argument is not an instance of URIRef, it's a {}".format(type(node)))

        if not isinstance(predicateword, str):
            raise RuntimeError("2nd argument is not an instance of str, it's a {}".format(type(predicateword)))

        node_uripart = node.uri
        self.combined_uri = '{}/{}'.format(node_uripart, predicateword)
        # if the current URI is different from the last one reset counter

    def __str__(self):
        return "<{}/{}>".format(self.combined_uri, self.count)


class BNodeRestart(_BNodeBasic):
    """Class for BNodes where the running number resets as soon as one of the arguments changes. These are not real blanknodes as defined in RDF but are constructed as:
    <SUBJECTURI + PREDICATEWORD + RUNNINGNUMBER>.

    Args:
        node: URIRef: subject to which the BNode should be attached
        predicateword: str: name of the property that describes the blanknode

    Returns:
        __str__: writes out the BNode URI
    """
    last_combined_uri = None

    def __init__(self, node, predicateword):
        _BNodeBasic.__init__(self, node, predicateword)
        if self.combined_uri != BNodeRestart.last_combined_uri:
            _BNodeBasic.counter = 0
            BNodeRestart.last_combined_uri = self.combined_uri

        #start counting at 1
        _BNodeBasic.counter += 1
        self.count = _BNodeBasic.counter

    def __str__(self):
        return(_BNodeBasic.__str__(self))


class BNodeContinuous(_BNodeBasic):
    """Class for BNodes where the running number is continuous. These are not real blanknodes as defined in RDF but are constructed as:
    <SUBJECTURI + PREDICATEWORD + RUNNINGNUMBER>.

    Args:
        node: URIRef: subject to which the BNode should be attached
        predicateword: str: name of the property that describes the blanknode

    Returns:
        __str__: writes out the BNode URI
    """
    def __init__(self, node, predicateword):
        _BNodeBasic.__init__(self, node, predicateword)
        _BNodeBasic.counter += 1
        self.count = _BNodeBasic.counter

    def __str__(self):
        return(_BNodeBasic.__str__(self))


class Literal(object):

    def __init__(self, st, datatype=None, language=None):
        self.typesuffix = ''

        if not isinstance(st, str) and not isinstance(st, unicode):
            raise RuntimeError("'{}' is not a string/unicode, it's a {}".format(st, type(st)))

        self.st = st.replace('\r', '').replace("\\", '\\\\').replace('"', '\\"')  # replace a backslash or " with backslashed characters to escape them
        self.datatype = datatype
        if self.datatype == 'date':
            self.typesuffix = '^^xsd:date'
        elif self.datatype == 'integer':
            self.typesuffix = '^^xsd:integer'
        elif datatype and datatype not in ['date', 'integer']:
            raise RuntimeError("'{}' is not a supported datatype".format(self.datatype))

        if language is not None:
            if language in languagetags:
                self.typesuffix = '@' + language
            else:
                raise RuntimeError("'{}' is not a supported language".format(language))

    def __str__(self):
        if '\n' in self.st:
            return '"""{}"""{}'.format(self.st, self.typesuffix)
        else:
            return '"{}"{}'.format(self.st, self.typesuffix)


class Namespace(object):

    def __init__(self, uri, ttl_prefix=None):
        self.uri = uri
        self.ttl_prefix = ttl_prefix

    def __str__(self):
        return '@prefix {}: <{}> .\n'.format(self.ttl_prefix, self.uri)

    def __getitem__(self, spec):
        if not isinstance(spec, str):
            raise RuntimeError("'{}' is not a string, it's a {}".format(spec, type(spec)))

        if self.ttl_prefix and not(spec and (spec[0].isdigit() or spec[0] == '-')) and not any(x in spec for x in ['#', '%', '.', '/']):  # 2 rules: first value after prefix can't be a digit, # or % cant be in suffix after prefix

            return self.ttl_prefix + ":" + spec
        else:
            return URIRef(self.uri + spec)


RDF = Namespace('http://www.w3.org/1999/02/22-rdf-syntax-ns#')
RDF.type = RDF['type']
RDFS = Namespace('http://www.w3.org/2000/01/rdf-schema#')
RDFS.label = RDFS['label']


class Graph(object):

    def __init__(self, out, federated=True):
        self.out = out
        self.last_subj = None
        self.last_pred = None
        self.federated = federated
        self.others = []

    def serialize(self):
        if self.last_subj:
            self.out.write('.\n')
        self.dump_others()

    def dump_others(self):
        for tpl in self.others:
            subj = str(tpl[0])
            pred = str(tpl[1])
            obj = str(tpl[2])
            self.out.write('{}\t{}\t{}.\n'.format(subj, pred, obj))
        self.others = []

    def add_can_be_none(self, tpl):
        if tpl[2] is None:
            return
        else:
            lit = Literal(tpl[2])
            newtpl = (tpl[0], tpl[1], lit)
        self.add((newtpl))

    def add(self, tpl, *others):
        if isinstance(tpl, Namespace):
            self.out.write(str(tpl))
        else:
            subj = str(tpl[0])
            pred = str(tpl[1])
            obj = str(tpl[2])

            if subj != self.last_subj:
                if self.last_subj:
                    self.out.write('.\n')
                self.dump_others()
                self.last_subj = subj
                self.last_pred = pred
                self.out.write('{}\t{}\t{}'.format(subj, pred, obj))
            elif pred != self.last_pred:
                self.last_pred = pred
                self.out.write(';\n\t{}\t{}'.format(pred, obj))
            else:
                self.out.write(',\n\t\t{}'.format(obj))
        for other in others:  # postpone these
            self.others.append(other)

    def add_remote_object(self, tpl, endpoint='public', *others):
        if not self.federated:
            self.add(tpl, *others)
        else:
            if isinstance(tpl, Namespace):
                self.add(tpl, *others)
            else:
                self.add(tpl, (tpl[2], URIRef('http://ns.ontoforce.com/2013/disqover#inRemote'), Literal(endpoint)), *others)


class NtGraph(object):

    def __init__(self, out):
        self.out = out

    def serialize(self):
        pass

    def add(self, tpl):
        if isinstance(tpl, Namespace):
            raise RuntimeError('NT format does not use Namespace')
        else:
            subj = str(tpl[0])
            pred = str(tpl[1])
            obj = str(tpl[2])
            self.out.write('{}\t{}\t{}.\n'.format(subj, pred, obj))


# this list is based on the ISO 639-1 standard, see languages.txt
languagetags = ['ab', 'aa', 'af', 'ak', 'sq', 'am', 'ar', 'an', 'hy', 'as', 'av', 'ae', 'ay', 'az', 'bm', 'ba', 'eu', 'be', 'bn', 'bh',
                'bi', 'bs', 'br', 'bg', 'my', 'ca', 'ch', 'ce', 'ny', 'zh', 'cv', 'kw', 'co', 'cr', 'hr', 'cs', 'da', 'dv', 'nl', 'dz',
                'en', 'eo', 'et', 'ee', 'fo', 'fj', 'fi', 'fr', 'ff', 'gl', 'ka', 'de', 'el', 'gn', 'gu', 'ht', 'ha', 'he', 'hz', 'hi',
                'ho', 'hu', 'ia', 'id', 'ie', 'ga', 'ig', 'ik', 'io', 'is', 'it', 'iu', 'ja', 'jv', 'kl', 'kn', 'kr', 'ks', 'kk', 'km',
                'ki', 'rw', 'ky', 'kv', 'kg', 'ko', 'ku', 'kj', 'la', 'lb', 'lg', 'li', 'ln', 'lo', 'lt', 'lu', 'lv', 'gv', 'mk', 'mg',
                'ms', 'ml', 'mt', 'mi', 'mr', 'mh', 'mn', 'na', 'nv', 'nd', 'ne', 'ng', 'nb', 'nn', 'no', 'ii', 'nr', 'oc', 'oj', 'cu',
                'om', 'or', 'os', 'pa', 'pi', 'fa', 'pl', 'ps', 'pt', 'qu', 'rm', 'rn', 'ro', 'ru', 'sa', 'sc', 'sd', 'se', 'sm', 'sg',
                'sr', 'gd', 'sn', 'si', 'sk', 'sl', 'so', 'st', 'es', 'su', 'sw', 'ss', 'sv', 'ta', 'te', 'tg', 'th', 'ti', 'bo', 'tk',
                'tl', 'tn', 'to', 'tr', 'ts', 'tt', 'tw', 'ty', 'ug', 'uk', 'ur', 'uz', 've', 'vi', 'vo', 'wa', 'cy', 'wo', 'fy', 'xh',
                'yi', 'yo', 'za', 'zu']
