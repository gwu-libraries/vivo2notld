from SPARQLWrapper import SPARQLWrapper


def query(endpoint, username, password, construct_query):
    sparql = SPARQLWrapper(endpoint)
    sparql.addParameter("email", username)
    sparql.addParameter("password", password)
    sparql.setQuery(construct_query)
    sparql.setMethod("POST")
    return sparql.queryAndConvert()
