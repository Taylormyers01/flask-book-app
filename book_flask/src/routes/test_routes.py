from flask import Blueprint, request, jsonify, render_template


test_bp = Blueprint('test', __name__)

@test_bp.route("/drop", methods=["POST"])
def drop():
    data = request.get_json()
    item = data.get("item")
    target = data.get("target")
    # Do something server-side (log, DB update, etc.)
    print(f"Item dropped: {item} onto {target}")
    return jsonify({"status": "ok", "message": f"{item} dropped on {target}"})


