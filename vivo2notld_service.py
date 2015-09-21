from flask import Flask, render_template, request, session, Response, flash, Markup
import argparse
from vivo2notld.definitions import definitions
from vivo2notld.utility import execute

formats = {
    "xml": "text/xml",
    "json": "text/json",
    "yaml": "text/yaml"
}

app = Flask(__name__)
default_definition = None
default_subject_namespace = None
default_subject_identifier = None
default_endpoint = None
default_username = None
default_password = None
default_format = None


def get_definitions():
    return {definition : definition.replace("_", " ") for definition in definitions}

@app.route('/', methods=["GET"])
def crosswalk_form(output=None, obj=None, graph=None, query=None):
    return render_template("crosswalk_form.html",
                           definitions=get_definitions(),
                           definition=session.get("definition") or default_definition,
                           subject_namespace=session.get("subject_namespace") or default_subject_namespace,
                           subject_identifier=session.get("subject_identifier") or default_subject_identifier,
                           endpoint=session.get("endpoint") or default_endpoint,
                           username=session.get("username") or default_username,
                           password=session.get("password") or default_password,
                           format=session.get("format") or default_format,
                           output_html=session.get("output_html", True),
                           output=output,
                           obj=obj,
                           graph=graph.serialize(format="turtle") if graph else None,
                           query=query)

@app.route('/', methods=["POST"])
def crosswalk():
    session["definition"] = request.form.get("definition")
    session["subject_namespace"] = request.form.get("subject_namespace")
    session["subject_identifier"] = request.form.get("subject_identifier")
    session["endpoint"] = request.form.get("endpoint")
    session["username"] = request.form.get("username")
    session["password"] = request.form.get("password")
    session["format"] = request.form.get("format")
    session["output_html"] = True if "output_html" in request.form else False

    o, s, g, q = execute(definitions[request.form.get("definition", default_definition)],
                         request.form.get("subject_namespace", default_subject_namespace),
                         request.form.get("subject_identifier", default_subject_identifier),
                         request.form.get("endpoint", default_endpoint),
                         request.form.get("username", default_username),
                         request.form.get("password", default_password),
                         serialization_format=request.form.get("format", default_format))

    if "output_html" in request.form:
        return crosswalk_form(output=o, obj=s, graph=g, query=q)
    else:
        return Response(o, content_type=formats[request.form['format']])


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--debug", action="store_true")
    parser.add_argument("--port", type=int, default="5000", help="The port the service should run on. Default is 5000.")

    parser.add_argument("--format", default="json", choices=formats.keys(),
                        help="The format for serializing. Default is json.")
    parser.add_argument("--endpoint", dest="endpoint",
                        help="Endpoint for SPARQL Query of VIVO instance,e.g., http://localhost/vivo/api/sparqlUpdate.")
    parser.add_argument("--username", dest="username", help="Username for VIVO root.")
    parser.add_argument("--password", dest="password",
                        help="Password for VIVO root.")
    parser.add_argument("--namespace", default="http://vivo.mydomain.edu/individual/",
                        help="Namespace for the subject. Default is http://vivo.mydomain.edu/individual/.")
    parser.add_argument("--identifier", help="Identifier for the subject, e.g., n123.")
    parser.add_argument("--definition", default="person", choices=definitions.keys(),
                        help="Default is person.")

    #Parse
    args = parser.parse_args()

    app.debug = args.debug
    app.secret_key = "vivo2notld"

    default_definition = args.definition
    default_subject_namespace = args.namespace
    default_subject_identifier = args.identifier
    default_endpoint = args.endpoint
    default_username = args.username
    default_password = args.password
    default_format = args.format

    app.run(host="0.0.0.0", port=args.port)