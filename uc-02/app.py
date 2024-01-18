#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
# Project LAWrence 
# Use-case 01:
    - getSummary API
# Use-case 02:
    - getArticles API
    - getParagraphs API
"""


from flask import (
    Flask,
    request,
    jsonify,
    render_template
)

from tools import *


# Flask app
app = Flask(__name__)


# Index
@app.route('/')
def index():
    """
    Demo UI
    """

    try:
        return render_template('index.html')
    except Exception as e:
        print("\033[31m*** ERROR in /:", str(e), "\033[m")
        return jsonify({"error": str(e)}), 400


# UC-01 API-01
@app.route('/getSummary', methods=['POST'])
def getSummary():
    """
    Returns a summary in a bullet point list for the given legal text.
    """

    try:
        # Validate and parse input data
        summary_response = get_summary(
            user_request = UserRequest.Summary(**request.get_json())
        )
        return jsonify(summary_response.model_dump())

    except ValidationError as e:
        print("\033[31m*** Validation error in /getSummary:", str(e), "\033[m")
        return jsonify({"error": str(e)}), 400


# UC-02 API-01
@app.route('/getArticles', methods=['POST'])
def getArticles():
    """
    Used by the UI to retrieve the articles that fit the legal questions.
    """

    try:
        # Validate and parse input data
        articles_response = get_articles(
            user_request = UserRequest.Articles(**request.get_json())
        )
        return jsonify(articles_response.model_dump())

    except ValidationError as e:
        print("\033[31m*** Validation error in /getArticles:", str(e), "\033[m")
        return jsonify({"error": str(e)}), 400


# UC-02 API-02
@app.route('/getParagraphs', methods=['GET', 'POST'])
def getParagraphs():
    """
    Will return the articles with detailed paragraph text for a given paragraph number.
    If paragraph is not provided, a list of paragraphs in this article are returned."
    """

    try:
        # Validate and parse input data
        articles = fetch_paragraphs(
            user_request = UserRequest.Paragraphs(**request.get_json())
        )
        data = [article.model_dump() for article in articles]
        return jsonify(data)

    except ValidationError as e:
        print("\033[31m*** Validation error in /getParagraphs:", str(e), "\033[m")
        return jsonify({"error": str(e)}), 400


# main
if __name__ == '__main__':
    app.run(
        host = '0.0.0.0',
        port = 5000,
        debug = True
    )
    