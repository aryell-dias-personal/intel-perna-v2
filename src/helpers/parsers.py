from src.helpers.constants import MATRIX_FIELDS, AGENT_FIELDS, ASKED_POINT_FIELDS

def parseResult(routes, agents, localnames):
    return [
        {
            AGENT_FIELDS.ID: agents[i][AGENT_FIELDS.ID],
            AGENT_FIELDS.ASKED_POINT_IDS: [],
            AGENT_FIELDS.WATCHED_BY: [],
            AGENT_FIELDS.ROUTE: [localnames[idx] for idx in routes[i]]
        } for i in range(len(routes))
    ]