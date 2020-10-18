import os
import json
import base64
import traceback 
from flask import Flask, jsonify, request, make_response
from src.model.taco import TeamAntColonyOptimization
from src.helpers.constants import PAYLOAD, MATRIX_FIELDS
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
    evaluation = Evaluation.minmax()
    antSystem = TeamAntColonyOptimization(data[PAYLOAD.AGENTS], evaluation)
    loader = Loader(data[PAYLOAD.MATRIX])
    stopCriterion = StopCriterion.iteration_limit(3)
    solutions, score, track = antSystem.optimize(loader, stopCriterion)
    result = parseResult(solutions, data[PAYLOAD.AGENTS], data[PAYLOAD.MATRIX][MATRIX_FIELDS.LOCAL_NAMES])
    # notifyUser(result)
    return result

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