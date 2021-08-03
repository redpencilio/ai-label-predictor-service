import io
import json
import os
from string import Template
import torch
import numpy as np

from flask import request, jsonify

from helpers import log
from transformers import AutoTokenizer

from .file_handler import postfile, get_file_by_id
from .preprocessor import Preprocessor
from .model import BertClassifier
from .utils import seed_everything

import sys

# set path for torch load model dir
here = os.path.dirname(os.path.abspath(__file__))
sys.path.append(here)

seed_everything()
preprocessor = Preprocessor()
# load dutch tokenizer
tokenizer = AutoTokenizer.from_pretrained("GroNLP/bert-base-dutch-cased")


def get_model(file_id):
    try:
        phys_file = get_file_by_id(file_id)
        model_file = phys_file["results"]["bindings"][0]["uri"]["value"].replace("share://", "/share/")

        log("Loading from: " + str(model_file))
        r = torch.load(model_file)
        log(r)
        return r
    except Exception as e:
        log(e)
        return None


@app.route("/label", methods=["GET"])
def query_data():
    """
    Endpoint for loading data from triple store using a query file and converting it to json
    Accepted request arguments:
        - filename: filename that contains the query
        - limit: limit the amount of data retrieved per query execution, allows for possible pagination
        - global_limit: total amount of items to be retrieved
    :return: response from storing data in triple store, contains virtual file id and uri
    """

    # env arguments to restrict option usage
    try:
        text = request.args.get("text")
        model_file = request.args.get("model")

        if not (text and model_file):
            return "Missing argument", 400

        model = get_model(model_file)
        if not model:
            return f"Unable to load model from file with id {model_file}", 400
        model.eval()

        log(text)
        preprocessed = preprocessor(text)
        log(preprocessed)

        tokens = tokenizer(text, add_special_tokens=True, return_tensors="pt", max_length=512,
                           truncation=True, padding="max_length")
        predictions = model(**tokens)
        predictions = predictions.data.cpu().numpy()[0]
        best_prediction = model.id_dict[np.argmax(predictions)]

        return best_prediction, 200
    except Exception as e:
        return str(e), 400


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    """
    Default endpoint/ catch all
    :param path: requested path
    :return: debug information
    """
    return 'You want path: %s' % path, 404


if __name__ == '__main__':
    debug = os.environ.get('MODE') == "development"
    app.run(debug=debug, host='0.0.0.0', port=80)
