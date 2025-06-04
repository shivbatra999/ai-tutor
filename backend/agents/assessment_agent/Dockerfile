# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PORT 8080
# AGENT_NAME will be set in the Cloud Run service environment; this is a default for local build clarity.
ENV AGENT_NAME "AssessmentAgent"

# Set the working directory in the container
WORKDIR /usr/src/app

# Copy the agent's specific code into the container
COPY ./main.py /usr/src/app/main.py
COPY ./requirements.txt /usr/src/app/agent_requirements.txt

# Copy the global requirements file from the backend directory.
# This path assumes the Docker build context is the agent's directory (e.g., backend/agents/assessment_agent).
COPY ../../requirements.txt /usr/src/app/global_requirements.txt

# Install Python dependencies
# First, install agent-specific requirements (if any and if the file is not empty)
RUN if [ -s agent_requirements.txt ]; then pip install --no-cache-dir -r agent_requirements.txt; fi
# Then, install global backend requirements
RUN pip install --no-cache-dir -r global_requirements.txt

# Make port ${PORT} available to the world outside this container
EXPOSE ${PORT}

# Run Uvicorn server for FastAPI
# The --workers flag can be adjusted based on expected load and CPU resources.
# For a typical Cloud Run instance with 1 vCPU, 1-2 workers is common.
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "${PORT}", "--workers", "1"]
