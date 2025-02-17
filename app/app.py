from tasks import flask_app, run_spider_task, migrate_data
from celery.result import AsyncResult
from flask import request,jsonify 
    
@flask_app.route("/run-spider", methods=["POST"])
def run_spider_route():
    """
    API endpoint to trigger a Scrapy spider asynchronously.
    """
    spider_name = request.json.get("spider_name")
    if not spider_name:
        return jsonify({"error": "Spider name is required"}), 400

    task = run_spider_task.apply_async(args=[spider_name])
    return jsonify({"task_id": task.id, "status": "Spider started"}), 202

@flask_app.route("/migrate-data", methods=["POST"])
def migrate_data_route():
    """
    API endpoint to trigger the data migration process asynchronously.
    """
    task = migrate_data.apply_async()
    return jsonify({"task_id": task.id, "status": "Migration started"}), 202


if __name__ == "__main__":
    flask_app.run(debug=True)