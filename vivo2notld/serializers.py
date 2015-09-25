import json
import yaml
from xml.etree.ElementTree import Element, tostring
from xml.dom import minidom


def to_json(subj, indent=4):
    return json.dumps(subj, indent=indent)


def _prettify_xml(elem, indent):
    """
    Return a pretty-printed XML string for the Element.
    """
    rough_string = tostring(elem, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent=" " * indent)


def _process_elem(subj, tag=None, parent_elem=None):
    if "list" in subj:
        attrs = {
            "count": str(subj["count"])
        }
        if "offset" in subj:
            attrs["offset"] = str(subj["offset"])
        if "limit" in subj:
            attrs["limit"] = str(subj["limit"])
        elem = Element("list", attrs)
        for child_subj in subj["list"]:
            _process_elem(child_subj, parent_elem=elem)
        return elem
    elif isinstance(subj, dict):
        assert subj["type"]
        assert subj["uri"]
        elem = Element(subj["type"].lower(), {"uri": subj["uri"]})
        if parent_elem is not None:
            parent_elem.append(elem)
        for key, value in subj.items():
            if key not in ("type", "uri"):
                _process_elem(value, tag=key, parent_elem=elem)
        return elem
    elif isinstance(subj, list):
        assert tag is not None
        assert parent_elem is not None
        if isinstance(subj[0], dict):
            elem = Element(tag.lower())
            parent_elem.append(elem)
            for value in subj:
                _process_elem(value, parent_elem=elem)
        else:
            for value in subj:
                _process_elem(value, tag=tag, parent_elem=parent_elem)
    else:
        assert tag is not None
        assert parent_elem is not None
        elem = Element(tag.lower())
        parent_elem.append(elem)
        elem.text = subj


def to_xml(subj, indent=4):
    elem = _process_elem(subj)
    return _prettify_xml(elem, indent)


def to_yaml(subj, indent=4):
    return yaml.safe_dump(subj, indent=indent)