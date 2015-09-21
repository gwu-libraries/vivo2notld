from rdflib import Literal, URIRef, RDF
from datetime import datetime
from .namespaces import NOTLD


def transform(graph, starting_uri):
    return _transform(graph, URIRef(starting_uri))


def _transform(graph, starting_uriref):
    subject = {
        "uri": str(starting_uriref)
    }
    for subj, pred, obj in graph.triples((starting_uriref, None, None)):
        key = _extract_identifier(pred)
        #A marker
        if obj == RDF.List:
            if key not in subject:
                subject[key] = []
            elif not isinstance(subject[key], list):
                new_value = [subject[key]]
                subject[key] = new_value
        else:
            if isinstance(obj, Literal):
                value = obj.value
            #Type
            elif pred == NOTLD.type:
                value = _extract_identifier(obj)
            else:
                value = _transform(graph, obj)

            #Convert datetime to string
            if isinstance(value, datetime):
                value = value.isoformat()

            if key not in subject:
                subject[key] = value
            elif isinstance(subject[key], list):
                subject[key].append(value)
            else:
                new_value = [subject[key], value]
                subject[key] = new_value
    #Remove empty lists
    for key in list([k for k in subject if subject[k] == []]):
        del subject[key]

    return subject


def _extract_identifier(uriref):
    uri = uriref.toPython()
    pos = uri.rindex("/")
    if "#" in uri:
        pos = uri.rindex("#")
    return uri[pos + 1:]