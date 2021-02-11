class MATRIX_FIELDS:
    REGION = "region"
    ADJACENCY_MATRIX= "adjacencyMatrix"
    ASKED_POINTS = "askedPoints"

class USER_FIELDS:
    MESSAGING_TOKENS = "messagingTokens"
    EMAIL = "email"

class AGENT_FIELDS:
    ID = "_id"
    NUMBER_OF_PLACES = "places"
    GARAGE = "garage"
    ASKED_START_AT = "askedStartAt"
    ASKED_END_AT = "askedEndAt"
    EMAIL = "email"
    ASKED_POINT_IDS = "askedPointIds"
    WATCHED_BY = "watchedBy"
    FROM_EMAIL = "email"
    ROUTE = "route"
    PROCESSED = "processed"

class ROUTE_POINT_FIELDS:
    TIME = "time"
    LOCAL = "local"

class PAYLOAD:
    MATRIX = "matrix"
    AGENTS = "agents"

class TYPE:
    EXPEDIENT = "EXPEDIENT"
    ASKED_POINT = "ASKED_POINT"

class ASKED_POINT_FIELDS:
    ID = "_id"
    ORIGIN = "origin"
    DESTINY = "destiny"
    ASKED_START_AT = "askedStartAt"
    ASKED_END_AT = "askedEndAt"
    EMAIL = "email"
    ACTUAL_START_AT = "actualStartAt"
    ACTUAL_END_AT = "actualEndAt"
    AGENT_ID = "agentId"
    PROCESSED = "processed"

class ENCODED_NAMES:
    SEPARETOR = '<{*_-_*}>'

class ANT_CNFG:
    TIME_THRESHOLD = 1000

class DB_COLLECTIONS:
    AGENT= "agent"
    ASKED_POINT= "askedPoint"
    USER= "user"

class MESSAGES:
   class NEW_ROUTE:
        TITLE = 'Nova Rota'
        BODY = 'Já calculamos sua próxima rota, vem dar uma olhada!! 😉'
   class NEW_ASKED_POINT:
        TITLE = 'Seu Pedido'
        BODY = 'Seu pedido foi analisado, vem ver se tá tudo certo 😎'