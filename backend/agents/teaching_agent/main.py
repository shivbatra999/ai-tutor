from fastapi import FastAPI, Query, HTTPException
from pydantic import BaseModel, Field
import os
import base64 # Keep for PubSub even if not fully used in /explain
import json   # Keep for PubSub

app = FastAPI(
    title=os.getenv("AGENT_NAME", "TeachingAgent"),
    description="Teaching Agent for providing explanations and learning content.",
    version="0.1.0"
)

# --- Pub/Sub Message Handling (Structure from previous step) ---
class PubSubMessage(BaseModel):
    data: str
    attributes: dict | None = None
    message_id: str | None = Field(None, alias="messageId")
    publish_time: str | None = Field(None, alias="publishTime")
    class Config: populate_by_name = True

class PubSubEnvelope(BaseModel):
    message: PubSubMessage
    subscription: str

@app.get("/")
async def health_check():
    return {"status": "healthy", "agent_name": os.getenv("AGENT_NAME", "TeachingAgent")}

@app.post("/handle-pubsub/", summary="Handle incoming Pub/Sub messages for teaching tasks")
async def handle_pubsub_message(envelope: PubSubEnvelope):
    agent_name = os.getenv("AGENT_NAME", "TeachingAgent")
    print(f"[{agent_name}] Received Pub/Sub message on subscription: {envelope.subscription}")
    # Basic decoding and logging, actual processing to be added
    try:
        decoded_data = base64.b64decode(envelope.message.data).decode("utf-8")
        message_json = json.loads(decoded_data)
        print(f"[{agent_name}] Decoded Pub/Sub data: {message_json}")
    except Exception as e:
        print(f"[{agent_name}] Error processing Pub/Sub message: {e}")
        # Acknowledge to prevent retries for now
    return {"status": "success", "detail": "Pub/Sub message acknowledged by TeachingAgent."}

# --- New Direct HTTP Endpoint for Explanations ---
class ExplanationResponse(BaseModel):
    topic: str
    explanation: str
    user_id: str | None = None
    agent_version: str

@app.get("/explain/", response_model=ExplanationResponse, summary="Get an explanation for a topic")
async def get_explanation(
    topic: str = Query(..., description="The topic to explain", min_length=3, max_length=100),
    user_id: str | None = Query(None, description="Optional user ID for context", max_length=50)
):
    agent_name = os.getenv("AGENT_NAME", "TeachingAgent")
    print(f"[{agent_name}] GET /explain/ called. Topic: {topic}, User ID: {user_id}")

    # **Simulated Vertex AI Interaction**
    # In a real implementation, you would:
    # 1. Initialize the Vertex AI client (e.g., using google-cloud-aiplatform).
    #    - Consider environment variables for project ID, location, and credentials.
    # 2. Construct a prompt for the Gemini model based on the 'topic' and 'user_id'.
    # 3. Call the Gemini model to generate the explanation.
    # 4. Handle potential errors from the API call.

    simulated_explanation = (
        f"This is a **simulated explanation** for the topic: '{topic}'. "
        f"A real Vertex AI Gemini model would generate content here. "
        f"User ID: {user_id if user_id else 'N/A'}."
    )

    print(f"[{agent_name}] Generated simulated explanation for: {topic}")

    return ExplanationResponse(
        topic=topic,
        explanation=simulated_explanation,
        user_id=user_id,
        agent_version=app.version
    )

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8080))
    print(f"Starting TeachingAgent locally on port {port}. Access API docs at http://localhost:{port}/docs")
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
