import os
from flask import Flask, request, jsonify
from flask.ext.cors import cross_origin
from flask_cache_response_decorator import cache

from search import bb_search, SearchError

app = Flask(__name__)

SEARCH_URL = os.environ.get('SEARCH_URL')
DEBUG = os.environ.get('FLASK_DEBUG') is not None
PORT = int(os.environ.get('FLASK_PORT', '5000'))
CACHE_MAX_AGE = int(os.environ.get('CACHE_MAX_AGE', '0'))

@app.route('/')
def root():
    return "Nothing here to see"

@app.route('/search')
@cache(expires=CACHE_MAX_AGE)
@cross_origin()
def search():
    searchword = request.args.get('q')
    if not searchword:
        return jsonify({'message': 'q parameter is required'}), 400

    try:
        results = bb_search(searchword, SEARCH_URL)
        return jsonify(results)
    except SearchError, e:
        return jsonify({'message': e.message}), e.code

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT, debug=DEBUG)
