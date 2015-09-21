from __future__ import print_function
from vivo2notld.definitions import definitions
from vivo2notld.utility import execute
import argparse
import codecs



if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("definition", choices=definitions.keys())
    parser.add_argument("subject_namespace", help="For example, http://vivo.gwu.edu/individual/")
    parser.add_argument("subject_identifier", help="For example, n115")
    parser.add_argument("endpoint",
                        help="Endpoint for SPARQL Query of VIVO instance,e.g., http://localhost/vivo/api/sparqlQuery.")
    parser.add_argument("username", help="Username for VIVO root.")
    parser.add_argument("password", help="Password for VIVO root.")
    parser.add_argument("--format", choices=["json", "yaml", "xml", "nt", "pretty-xml", "trix"],
                        help="The format for serializing. Default is json.", default="json")
    parser.add_argument("--indent", default="4", type=int, help="Number of spaces to use for indents.")
    parser.add_argument("--file", help="Filepath to which to serialize.")
    parser.add_argument("--debug", action="store_true", help="Also output the query, result graph, and python object.")

    #Parse
    args = parser.parse_args()

    main_o, main_s, main_g, main_q = execute(definitions[args.definition], args.subject_namespace,
                                             args.subject_identifier, args.endpoint, args.username, args.password,
                                             serialization_format=args.format, indent=args.indent)

    if args.file:
        with codecs.open(args.file, "w") as out:
            out.write(main_o)
    else:
        print(main_o)

    if args.debug:
        print("""


PYTHON OBJECT:
{s}


RESULT GRAPH:
{g}


QUERY:
{q}
""".format(s=main_s, g=main_g.serialize(format="turtle"), q=main_q))


#TODO: Add to github
#TODO: Add to Travis
#TODO: Add datetime test