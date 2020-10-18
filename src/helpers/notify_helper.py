from src.helpers.constants import DB_COLLECTIONS, ENCODED_NAMES, ASKED_POINT_FIELDS, AGENT_FIELDS, USER_FIELDS, MESSAGES, ROUTE_POINT_FIELDS, TYPE
import firebase_admin
from firebase_admin import firestore
from firebase_admin import messaging

app = firebase_admin.initialize_app()

def buildMessage(token, title, body, time, nType):
    return messaging.Message( 
        android=messaging.AndroidConfig(
            notification=messaging.AndroidNotification(title=title, body=body, click_action="FLUTTER_NOTIFICATION_CLICK"),
        ),
        data={
            "time": str(time),
            "type": nType
        },
        token=token
    ) 
def decodePlace(place):
    return place.split(ENCODED_NAMES.SEPARETOR)[0]

def getOriginDestinyTime(route, origin, destiny):
    actualStartAt = None
    actualEndAt = None
    for point in route:
        if(point[ROUTE_POINT_FIELDS.LOCAL]==decodePlace(origin)):
            actualStartAt = point[ROUTE_POINT_FIELDS.TIME]
        elif(point[ROUTE_POINT_FIELDS.LOCAL]==decodePlace(destiny)):
            actualEndAt = point[ROUTE_POINT_FIELDS.TIME]
        if(actualStartAt and actualEndAt):
            break
    return actualStartAt, actualEndAt

def handleAskedPoint(agent, askedPointIds, askedPointsCollection, usersCollection):
    messages = []
    for askedPoint in askedPointIds:
        askedPointRef = askedPointsCollection.document(askedPoint)
        askedPoint = askedPointRef.get().to_dict()
        actualStartAt, actualEndAt = getOriginDestinyTime(agent[AGENT_FIELDS.ROUTE], askedPoint[ASKED_POINT_FIELDS.ORIGIN], askedPoint[ASKED_POINT_FIELDS.DESTINY])
        askedPointRef.set({
            ASKED_POINT_FIELDS.ACTUAL_START_AT: actualStartAt,
            ASKED_POINT_FIELDS.ACTUAL_END_AT: actualEndAt,
            ASKED_POINT_FIELDS.AGENT_ID: agent[AGENT_FIELDS.ID],
            ASKED_POINT_FIELDS.PROCESSED: True
        }, merge=True)
        user = usersCollection.where(USER_FIELDS.EMAIL, '==', askedPoint[ASKED_POINT_FIELDS.EMAIL]).limit(1).stream().__next__().to_dict()
        messages += [buildMessage(token,MESSAGES.NEW_ASKED_POINT.TITLE, MESSAGES.NEW_ASKED_POINT.BODY, askedPoint[ASKED_POINT_FIELDS.ACTUAL_START_AT], TYPE.ASKED_POINT) for token in user[USER_FIELDS.MESSAGING_TOKENS]]
    return messages

def notifyUser(result):
    messages = []
    db = firestore.client()
    askedPointsCollection = db.collection(DB_COLLECTIONS.ASKED_POINT)
    agentsCollection = db.collection(DB_COLLECTIONS.AGENT)
    usersCollection = db.collection(DB_COLLECTIONS.USER)
    for agent in result:
        agentRef = agentsCollection.document(agent[AGENT_FIELDS.ID])
        agentRef.set({ 
            AGENT_FIELDS.ROUTE: agent[AGENT_FIELDS.ROUTE],
            AGENT_FIELDS.ASKED_POINT_IDS: agent[AGENT_FIELDS.ASKED_POINT_IDS],
            AGENT_FIELDS.WATCHED_BY: agent[AGENT_FIELDS.WATCHED_BY],
            AGENT_FIELDS.PROCESSED: True
        }, merge=True)
        messages += handleAskedPoint(agent, agent[AGENT_FIELDS.ASKED_POINT_IDS], askedPointsCollection, usersCollection)
        agent = agentRef.get().to_dict()
        user = usersCollection.where(USER_FIELDS.EMAIL, '==', agent[AGENT_FIELDS.EMAIL]).limit(1).stream().__next__().to_dict()
        messages += [buildMessage(token,MESSAGES.NEW_ROUTE.TITLE, MESSAGES.NEW_ROUTE.BODY, agent[AGENT_FIELDS.ROUTE][0][ROUTE_POINT_FIELDS.TIME], TYPE.EXPEDIENT) for token in user[USER_FIELDS.MESSAGING_TOKENS]]
    messaging.send_all(messages)