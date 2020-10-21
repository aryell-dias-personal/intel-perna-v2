from src.helpers.constants import MATRIX_FIELDS, AGENT_FIELDS, ASKED_POINT_FIELDS

# TODO: mapear quem pediu solution deverá ser uma lista de start e endpoints do askedPoint
def parseResult(loader, routes, agents):
    return [
        {
            AGENT_FIELDS.ID: agents[i][AGENT_FIELDS.ID],
            AGENT_FIELDS.ASKED_POINT_IDS: [],
            AGENT_FIELDS.WATCHED_BY: [],
            AGENT_FIELDS.ROUTE: [loader.decodePlace(loader.encodedNames[idx]) for idx in routes[i]]
        } for i in range(len(routes))
    ]