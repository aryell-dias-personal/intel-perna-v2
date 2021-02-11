import os
import json
import base64
import traceback 
from flask import Flask, jsonify, request, make_response
from src.model.taco import TeamAntColonyOptimization
from src.helpers.constants import PAYLOAD
from src.data.evaluation import Evaluation
from src.data.loader import Loader
from src.data.stop import StopCriterion
from src.helpers.notify_helper import notifyUser
from src.helpers.parsers import parseResult
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)

def getRoutes(payload):
    print("PAYLOAD")
    print(payload)
    data = json.loads(payload)
    print("DATA")
    print(data)
    print("PREPARING_ANTS")
    evaluation = Evaluation.sumEvaluation()
    antSystem = TeamAntColonyOptimization(data[PAYLOAD.AGENTS], evaluation)
    print("LOADING_DATA")
    loader = Loader(data[PAYLOAD.MATRIX], data[PAYLOAD.AGENTS])
    stopCriterion = StopCriterion.iteration_limit(150)
    print("EXECUTING")
    solutions, score, times, track = antSystem.optimize(loader, stopCriterion)
    result = parseResult(loader, solutions, times, data[PAYLOAD.AGENTS])
    print("NOTIFYING")
    notifyUser(result)
    return result

@app.route("/", methods=["POST"])
def post():
    try:
        print("REQUEST")
        result = getRoutes(request.data)
        print("RESULT")
        print(result)
        return make_response(jsonify(
            success=True,
            result=result
        ), 200)
    except Exception as err:
        print("ERROR")
        print(traceback.format_exc())
        return make_response(jsonify(
            success=False,
            message=traceback.format_exc()
        ), 500)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))