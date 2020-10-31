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
    data = json.loads(payload)
    evaluation = Evaluation.sumEvaluation()
    antSystem = TeamAntColonyOptimization(data[PAYLOAD.AGENTS], evaluation)
    loader = Loader(data[PAYLOAD.MATRIX], data[PAYLOAD.AGENTS])
    stopCriterion = StopCriterion.iteration_limit(150)
    solutions, score, times, track = antSystem.optimize(loader, stopCriterion)
    result = parseResult(loader, solutions, times, data[PAYLOAD.AGENTS])
    notifyUser(result)
    return result

# TODO: dar uma lida em: 
# https://cloud.google.com/run/docs/triggering/pubsub-push?hl=pt-br#run_pubsub_handler-python
# https://cloud.google.com/run/docs/gke/enabling-on-existing-clusters
# no entanto parece mais adequado colocar em App Engine
@app.route("/", methods=["POST"])
def post():
    try:
        result = getRoutes(request.data)
        return make_response(jsonify(
            success=True,
            result=result
        ), 200)
    except Exception as err:
        message = err.args[0] if err.args and err.args[0] else "Internal Server Error"
        return make_response(jsonify(
            success=False,
            message=message,
            stack=traceback.format_exc()
        ), 500)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))