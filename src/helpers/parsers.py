from src.helpers.constants import MATRIX_FIELDS, AGENT_FIELDS, ASKED_POINT_FIELDS, ROUTE_POINT_FIELDS

def parseResult(loader, routes, times, agents):
    result = []
    for i in range(len(routes)):
        route = [{
            ROUTE_POINT_FIELDS.LOCAL: loader.decodePlace(loader.encodedNames[routes[i][idx]]),
            ROUTE_POINT_FIELDS.TIME: times[i][idx]
        } for idx in range(len(routes[i]))]
        visitedAskedPoints = loader.askedPointFromRoute(routes[i])
        fromEmail = agents[i][AGENT_FIELDS.FROM_EMAIL]
        result.append({
            AGENT_FIELDS.ID: agents[i][AGENT_FIELDS.ID],
            AGENT_FIELDS.ASKED_POINT_IDS: [askedPoint[ASKED_POINT_FIELDS.ID] for askedPoint in visitedAskedPoints],
            AGENT_FIELDS.WATCHED_BY: [askedPoint[ASKED_POINT_FIELDS.EMAIL] for askedPoint in visitedAskedPoints] + ([fromEmail] if fromEmail else []),
            AGENT_FIELDS.ROUTE: route
        })
    return result