from flask import Blueprint, jsonify, request, current_app
from .tasks import run_spider

main = Blueprint("main", __name__)

@main.route("/")
def home():
    return jsonify({"message": "Welcome to the Scraping Engine API!"})

@main.route("/run-spider", methods=["POST"])
def run_spider_route():
    spider_name = request.json.get("spider_name")
    if not spider_name:
        return jsonify({"error": "Spider name is required"}), 400

    result = run_spider(spider_name)
    return jsonify({"status": "Spider started", "spider_name": spider_name, "result": result})
