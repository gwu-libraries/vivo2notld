from SPARQLWrapper import SPARQLWrapper, JSON


def query(endpoint, username, password, construct_query):
    sparql = SPARQLWrapper(endpoint)
    sparql.addParameter("email", username)
    sparql.addParameter("password", password)
    sparql.setQuery(construct_query)
    sparql.setMethod("POST")
    return sparql.queryAndConvert()


def select_query(endpoint, username, password, select_query):
    sparql = SPARQLWrapper(endpoint)
    sparql.addParameter("email", username)
    sparql.addParameter("password", password)
    sparql.setQuery(select_query)
    sparql.setMethod("POST")
    sparql.setReturnFormat(JSON)
    return sparql.queryAndConvert()
