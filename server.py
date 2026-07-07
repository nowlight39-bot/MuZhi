import json
import hmac
import hashlib
import base64
import time
import os
import uuid
import logging
from flask import Flask, request, jsonify, Response, stream_with_context
from knowledge import query_knowledge

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

app = Flask(__name__)

SECRET_KEY = os.environ.get("A2A_SECRET_KEY", "your-secret-key-here")
ACCESS_KEY = os.environ.get("A2A_ACCESS_KEY", "your-access-key-here")
ALLOW_NO_AUTH = os.environ.get("ALLOW_NO_AUTH", "true").lower() == "true"
TIMESTAMP_TOLERANCE = 5 * 60


def verify_signature():
    auth = request.headers.get("Authorization", "")
    ts = request.headers.get("X-Timestamp", "")
    sign = request.headers.get("X-Sign", "")
    if ALLOW_NO_AUTH:
        return True, "OK"
    if not all([auth, ts, sign]):
        return False, "Missing auth headers"
    if auth != f"AK {ACCESS_KEY}":
        return False, "Invalid access key"
    try:
        if abs(time.time() * 1000 - int(ts)) > TIMESTAMP_TOLERANCE * 1000:
            return False, "Request expired"
    except ValueError:
        return False, "Invalid timestamp"
    expected = base64.b64encode(
        hmac.new(SECRET_KEY.encode(), ts.encode(), hashlib.sha256).digest()
    ).decode()
    if sign != expected:
        return False, "Signature verification failed"
    return True, "OK"


def extract_text(params):
    message = params.get("message", {})
    if isinstance(message, str):
        return message
    parts = message.get("parts") or []
    for p in parts:
        if isinstance(p, dict):
            if p.get("kind") == "text":
                return p.get("text", "")
            if p.get("type") in ("text", "Text"):
                return p.get("text", "")
    for p in parts:
        if isinstance(p, dict) and p.get("kind") == "data":
            data = p.get("data", {})
            if isinstance(data, dict):
                text = data.get("text", "")
                if text:
                    return text
    return message.get("text", "")


@app.route("/agent/message", methods=["POST"])
def agent_message():
    ok, msg = verify_signature()
    if not ok:
        return jsonify({"jsonrpc": "2.0", "error": {"code": -32000, "message": msg}}), 401

    body = request.get_json(force=True, silent=True)
    if not body:
        return jsonify({"jsonrpc": "2.0", "id": None, "error": {"code": -32700, "message": "Parse error"}}), 400

    logger.info(f"Request: {json.dumps(body, ensure_ascii=False)}")

    method = body.get("method", "")
    params = body.get("params", {}) or {}
    req_id = body.get("id", 1)

    if method == "initialize":
        return jsonify({
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "version": "1.0",
                "agentSessionId": str(uuid.uuid4()).replace("-", ""),
                "agentSessionTtl": 604800
            }
        })
    elif method == "notifications/initialized":
        return "", 200
    elif method == "message/stream":
        return handle_stream(params, req_id)
    elif method == "tasks/cancel":
        task_id = params.get("id", str(uuid.uuid4()))
        return jsonify({
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "taskId": task_id,
                "kind": "status-update",
                "final": True,
                "status": {"state": "cancelled"}
            }
        })
    elif method == "clearContext":
        return jsonify({
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {}
        })
    else:
        return jsonify({
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "taskId": str(uuid.uuid4()),
                "kind": "status-update",
                "final": True,
                "status": {"state": "completed"}
            }
        })


def handle_stream(params, req_id):
    text = extract_text(params)
    task_id = params.get("id", str(uuid.uuid4()))
    logger.info(f"Stream query: {text}")

    result = query_knowledge(text)
    answer = result["answer"]
    artifact_id = str(uuid.uuid4())

    def generate():
        working = {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "taskId": task_id,
                "kind": "status-update",
                "final": False,
                "status": {
                    "message": {
                        "role": "agent",
                        "parts": [{"kind": "text", "text": "正在查询..."}]
                    },
                    "state": "working"
                }
            }
        }
        yield f"data: {json.dumps(working, ensure_ascii=False)}\n\n"

        paragraphs = answer.split("\n")
        for i, para in enumerate(paragraphs):
            chunk = para + ("\n" if i < len(paragraphs) - 1 else "")
            if not chunk.strip():
                continue
            is_last = (i == len(paragraphs) - 1)
            artifact_event = {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "taskId": task_id,
                    "kind": "artifact-update",
                    "append": True,
                    "lastChunk": is_last,
                    "final": is_last,
                    "artifact": {
                        "artifactId": artifact_id,
                        "parts": [{"kind": "text", "text": chunk}]
                    }
                }
            }
            yield f"data: {json.dumps(artifact_event, ensure_ascii=False)}\n\n"

        done = {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "taskId": task_id,
                "kind": "status-update",
                "final": True,
                "status": {"state": "completed"}
            }
        }
        yield f"data: {json.dumps(done, ensure_ascii=False)}\n\n"
        yield "data: [DONE]\n\n"

    return Response(
        stream_with_context(generate()),
        mimetype="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
            "Connection": "keep-alive"
        }
    )


@app.route("/health", methods=["GET"])
def health():
    unis = query_knowledge("", list_only=True)
    return jsonify({
        "status": "ok",
        "universities_count": len(unis),
        "universities": unis
    })


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"Server starting on port {port}")
    app.run(host="0.0.0.0", port=port, debug=True)
