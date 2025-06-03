from flask import Flask, request, jsonify
import os
import json
import base64

app = Flask(__name__)

@app.route('/', methods=['POST'])
def handle_pubsub_message():
    envelope = request.get_json()
    if not envelope:
        msg = "no Pub/Sub message received"
        print(f"error: {msg}")
        return f"Bad Request: {msg}", 400

    if not isinstance(envelope, dict) or "message" not in envelope:
        msg = "invalid Pub/Sub message format"
        print(f"error: {msg}")
        return f"Bad Request: {msg}", 400

    pubsub_message = envelope["message"]

    data = {}
    if isinstance(pubsub_message, dict) and "data" in pubsub_message:
        try:
            data = json.loads(base64.b64decode(pubsub_message["data"]).decode("utf-8"))
        except Exception as e:
            print(f"Error decoding message data: {e}")
            data_str = base64.b64decode(pubsub_message["data"]).decode("utf-8")
            print(f"Received data string: {data_str}")
            # Placeholder for handling non-JSON data if necessary

    message_id = pubsub_message.get("message_id")
    publish_time = pubsub_message.get("publish_time")

    print(f"Received Pub/Sub message ID: {message_id} published at {publish_time}")
    print(f"Data: {json.dumps(data, indent=2)}")

    # Placeholder for Teaching Agent specific logic
    # This agent will generate and deliver lesson content.

    return jsonify({"status": "success", "message_id": message_id}), 200

if __name__ == "__main__":
    PORT = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=PORT, debug=True)
