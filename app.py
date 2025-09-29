from datetime import datetime, timezone
from flask import Flask, request, jsonify
from flask_cors import CORS
from pydantic import ValidationError
from models import SurveySubmission, StoredSurveyRecord
from storage import append_json_line
import hashlib

app = Flask(__name__)
CORS(app, resources={r"/v1/*": {"origins": "*"}})  # allow cross-origin requests

# Simple health check
@app.route("/ping", methods=["GET"])
def ping():
    return jsonify({
        "status": "ok",
        "message": "API is alive",
        "utc_time": datetime.now(timezone.utc).isoformat()
    })


# Utility function to hash values
def sha256_hash(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


@app.post("/v1/survey")
def submit_survey():
    payload = request.get_json(silent=True)
    if payload is None:
        return jsonify({"error": "invalid_json", "detail": "Body must be application/json"}), 400

    # Validate input
    try:
        submission = SurveySubmission(**payload)
    except ValidationError as ve:
        return jsonify({"error": "validation_error", "detail": ve.errors()}), 422

    # Compute submission_id
    if getattr(submission, "submission_id", None):
        submission_id = submission.submission_id
    else:
        timestamp = datetime.now().strftime("%Y%m%d%H")
        submission_id = sha256_hash(submission.email + timestamp)

    # Create record with hashed PII and optional user_agent
    record = StoredSurveyRecord(
        **submission.dict(exclude={"email", "age", "submission_id"}),  # remove raw email/age/submission_id
        email=sha256_hash(submission.email),
        age=sha256_hash(str(submission.age)),
        submission_id=submission_id,
        received_at=datetime.now(timezone.utc),
        ip=request.headers.get("X-Forwarded-For", request.remote_addr or "")
    )

    append_json_line(record.dict())
    return jsonify({"status": "ok"}), 201


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
