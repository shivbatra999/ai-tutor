from fastapi import FastAPI, Request, HTTPException
from pydantic import BaseModel, Field
import base64
import json
import os

# Placeholder: For environment variables if using .env locally for an agent
# from dotenv import load_dotenv
# load_dotenv()

app = FastAPI(
    title=os.getenv("AGENT_NAME", "FeedbackAgent"), # Specific default for clarity
    version="0.1.0"
)

# Define a Pydantic model for the Pub/Sub message structure
class PubSubMessage(BaseModel):
    data: str  # Base64-encoded data
    attributes: dict | None = None
    message_id: str | None = Field(None, alias="messageId")
    publish_time: str | None = Field(None, alias="publishTime")

    class Config:
        populate_by_name = True

class PubSubEnvelope(BaseModel):
    message: PubSubMessage
    subscription: str

@app.get("/")
async def health_check():
    return {"status": "healthy", "agent_name": os.getenv("AGENT_NAME", "FeedbackAgent")}

@app.post("/handle-pubsub/", summary="Handle incoming Pub/Sub messages")
async def handle_pubsub_message(envelope: PubSubEnvelope):
    agent_name = os.getenv("AGENT_NAME", "FeedbackAgent")
    print(f"[{agent_name}] Received message on subscription: {envelope.subscription}")
    print(f"[{agent_name}] Message ID: {envelope.message.message_id}")

    decoded_data = ""
    message_json = None
    try:
        decoded_data = base64.b64decode(envelope.message.data).decode("utf-8")
        message_json = json.loads(decoded_data)
        print(f"[{agent_name}] Decoded message data: {message_json}")
    except Exception as e:
        print(f"[{agent_name}] Error decoding or parsing JSON from message data: {e}")
        print(f"[{agent_name}] Raw decoded data string: {decoded_data}")
        return {"status": "error", "detail": "Error processing message data", "message_id": envelope.message.message_id}

    # TODO: Implement FeedbackAgent-specific logic here
    # e.g., process `message_json` based on "QuizAttemptSubmitted"
    # - Evaluate student's answers.
    # - Provide constructive feedback using LLM.
    # - Update Firestore with results and progress.
    # - Publish "FeedbackProvided" message.
    # - Potentially publish "FurtherStudyRecommended".

    print(f"[{agent_name}] Successfully processed message ID: {envelope.message.message_id}")
    return {"status": "success", "message_id": envelope.message.message_id, "processed_data": message_json}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8080))
    agent_name_for_log = os.getenv("AGENT_NAME", "FeedbackAgent")
    print(f"Starting {agent_name_for_log} locally on port {port}...")
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
