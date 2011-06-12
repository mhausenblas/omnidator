# JsonLDSerializer.py
# Author: Richard Jones
#
# This serialiser will output an RDF Graph as a JSON-LD formatted document.
# See:
#   http://json-ld.org/
#
# TODO:
#   This code writes the entire JSON object into memory before serialising,
#   but we should consider streaming the output to deal with arbitrarily
#   large graphs
"""
Example usage:

from rdflib import Graph, plugin
from rdflib.serializer import Serializer
g = Graph()
g.parse("/home/richard/Code/Internal/RDFLib/test.rdf")
plugin.register("json-ld", Serializer, "JsonLDSerializer", "JsonLDSerializer")
g.serialize("/home/richard/Code/Internal/RDFLib/json-ld2.json", "json-ld", use_type_coercion=True, use_language_coercion=True)
"""

from rdflib.serializer import Serializer

from rdflib.term import URIRef, BNode, Literal

try:
    import json
except ImportError:
    import simplejson as json

class JsonLDSerializer(Serializer):

    def __init__(self, store):
        super(JsonLDSerializer, self).__init__(store)
        self.__stream = None
        self.__serialized = None
        self.default_vocab = None

    def serialize(self, stream, base=None, encoding=None, **args):
        self.base = base
        self.write = lambda u: stream.write(u.encode(self.encoding, 'replace'))

        self.__stream = stream
        self.__serialized = {}

        # get the relevant bits out of the keyword args
        self.default_vocab = args.get("default_vocab")
        self.use_type_coercion = args.get("use_type_coercion", False)
        self.use_language_coercion = args.get("use_language_coercion", False)
        
        # create a json object for us to work on
        self.jsonObj = {}

        # we need a place to store the coerced types
        self.coerced_types = {}
        
        # first add the namespace declarations
        self.add_namespaces()

        # add a place in the jsonObj for the graph
        self.jsonObj["@"] = []

        # now go through each subject and create its dictionary for the graph
        for subject in self.store.subjects():
            self.handle_subject(subject)

        # now add the coerced types to the json object
        self.add_coerced_types()

        srlzd = json.dumps(self.jsonObj, indent=2)
        self.write(srlzd)
        del self.__serialized

    def add_namespaces(self):
        namespaces = {}

        # get the namespaces out of the graph
        for prefix, uri in self.store.namespaces():
            namespaces[prefix] = uri

        # add the #base namespace
        if self.base is not None:
            namespaces["#base"] = self.base

        # note, we don't use a type coercion header or the #vocab header
        # in the serialiser

        # add the namespaces to the jsonObj
        self.jsonObj["#"] = namespaces

    def handle_predicate(self, pred):
        # first convert the predicate to a pure string before we start work
        predname = str(pred)

        # determine if the predicate is rdf:type
        predname = self.handle_rdf_type(predname)

        # then, get the CURIE of the predicate if possible
        predname = self.curie(predname)

        # next try to relativise the predicate
        predname = self.relativize(predname)

        return predname

    def handle_subject(self, subject):
        if subject in self.__serialized:
            # already dealt with
            return

        # register that we've dealt with this subject
        self.__serialized[subject] = 1
        
        if isinstance(subject, URIRef):
            # if the subject is a URI relativize it
            uri = self.relativize(subject)
        else:
            # Blank Node
            uri = '%s' % subject.n3()
          
        subject_dict = {}
        subject_dict["@"] = uri

        # go through the predicates and objects and build a dictionary
        # for each predicate with an array of values        
        pred_dict = {}
        for pred, obj in self.store.predicate_objects(subject):
            
            # normalise/prepare the predicate
            predname = self.handle_predicate(pred)

            # now deal with the object
            obj_value = self.handle_object(predname, obj)

            if subject_dict.has_key(predname):
                if not isinstance(subject_dict[predname], list):
                    # if the value is a string replace it with a single value array
                    existing_value = subject_dict[predname]
                    subject_dict[predname] = [existing_value]
                # append the new value to the array
                subject_dict[predname].append(obj_value)
            else:
                # in the case of a single value, no array
                subject_dict[predname] = obj_value
        
        # finally add the dictionary to the graph
        self.jsonObj["@"].append(subject_dict)

    def handle_object(self, predname, obj):
        #print predname + " - " + str(obj)
        o = None
        if isinstance(obj, Literal):
            # NOTE: this if/else test works ONLY because obj.datatype and obj.language are
            # mutually exclusive
            if self.use_type_coercion and obj.datatype is not None:
                # just use the string representation
                o = str(obj)
                # register the type for the field
                self.coerced_types[predname] = str(obj.datatype)
            elif self.use_language_coercion and obj.language is not None:
                # just use the string representation
                o = str(obj)
                # FIXME: language coercion in this case just omits the language at this stage
            else:
                o = obj.n3()
                # in this case, we need to be careful when removing the " marks
                # strip the leading quote
                o = o[1:]
                # strip the "@ string and replace with @
                o = o.replace("\"@", "@")
                # strinp the "^^ and replace with ^^
                o = o.replace("\"^^", "^^")
                # chomp the final "
                if o.endswith("\""):
                    o = o[:len(o) - 1]
        else:
            o = obj.n3()
        #print o
        return o

    def add_coerced_types(self):
        if self.use_type_coercion and len(self.coerced_types.keys()) > 0:
            self.jsonObj["#"]["#types"] = (self.coerced_types)    

    def curie(self, uri):
        for prefix, identifier in self.store.namespaces():
            if uri.startswith(identifier):
                uri = uri.replace(identifier, prefix + ":")
                break
        return uri

    def handle_rdf_type(self, uri):
        if str(uri) == "http://www.w3.org/1999/02/22-rdf-syntax-ns#type" or str(uri) == "rdf:type":
            return "a"
        return uri

    def relativize(self, uri):
        base = self.base
        if base is not None and uri.startswith(base):
            uri = uri.replace(base, "", 1)
        return uri

