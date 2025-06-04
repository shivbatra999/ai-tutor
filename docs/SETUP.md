# Setup Guide

This document provides instructions for setting up the development environment.

## 1. Prerequisites
- [Node.js and npm](https://nodejs.org/) (for Firebase CLI and frontend)
- [Python](https://www.python.org/) (for backend agents)
- [Docker](https://www.docker.com/products/docker-desktop) (for running agents in containers)
- [Google Cloud SDK (gcloud CLI)](https://cloud.google.com/sdk/docs/install) (for deploying to Google Cloud eventually, and for Application Default Credentials)

## 2. Firebase Setup (Local Emulation and Project Configuration)

This project uses Firebase for Authentication and Firestore as its database. For local development, we will use the Firebase Emulator Suite.

### 2.1. Install Firebase CLI
If you haven't already, install the Firebase CLI globally:
```bash
npm install -g firebase-tools
```

### 2.2. Login to Firebase (Optional but Recommended)
Login to your Firebase account. This is needed if you plan to eventually connect to a real Firebase project.
```bash
firebase login
```

### 2.3. Initialize Firebase in Your Project (Conceptual - if you have a real project)
If you were connecting to a *real* Firebase project, you would typically run `firebase init` in the project root or a designated Firebase config directory. For this project, we primarily focus on the emulator setup first. The frontend and backend will need Firebase project configuration details (API keys, project ID) to connect to either the emulator or a live project.

**For Local Development with Emulators:**
You don't strictly need to run `firebase init firestore` or `firebase init auth` if you only intend to use the emulators with default settings initially. However, you do need a `firebase.json` file to configure the emulators.

Create a `firebase.json` file in the project root with the following content. **You will need to create this file manually.**
```json
{
  "firestore": {
    "rules": "firestore.rules",
    "indexes": "firestore.indexes.json"
  },
  "auth": {
  },
  "emulators": {
    "auth": {
      "port": 9099
    },
    "firestore": {
      "port": 8081
    },
    "ui": {
      "enabled": true,
      "port": 4000
    },
    "pubsub": {
        "port": 8085
    }
  }
}
```
*Important: We've set Firestore to port `8081` to avoid conflicts if an agent runs on the default `8080`. Adjust if necessary.*

Create a basic `firestore.indexes.json` in the project root (can be empty if no complex queries yet). **You will need to create this file manually.**
```json
{
  "indexes": [],
  "fieldOverrides": []
}
```

### 2.4. Starting the Firebase Emulators
Navigate to the project root directory (where `firebase.json` is located) and run:
```bash
firebase emulators:start --import=./firebase-emulator-data --export-on-exit=./firebase-emulator-data
```
- This command starts the emulators configured in `firebase.json`.
- Create an empty directory named `firebase-emulator-data` in the project root before running the command for the first time. This is where emulator data will be imported from and exported to.
- The Emulator UI will be available at `http://localhost:4000`.

### 2.5. Configuring Your Application to Use the Emulators

**Frontend (React - in `frontend/src/firebaseConfig.js` or similar - to be created later):**
When initializing Firebase in your React app, you'll need to point to the emulators.
Example:
```javascript
import { initializeApp } from "firebase/app";
import { getAuth, connectAuthEmulator } from "firebase/auth";
import { getFirestore, connectFirestoreEmulator } from "firebase/firestore";

const firebaseConfig = {
  apiKey: "YOUR_API_KEY_HERE", // Use your actual Firebase project config values
  authDomain: "YOUR_PROJECT_ID.firebaseapp.com",
  projectId: "YOUR_PROJECT_ID", // IMPORTANT: Use a consistent Project ID for emulators
  storageBucket: "YOUR_PROJECT_ID.appspot.com",
  messagingSenderId: "YOUR_MESSAGING_SENDER_ID",
  appId: "YOUR_APP_ID"
};

const app = initializeApp(firebaseConfig);
const auth = getAuth(app);
const db = getFirestore(app);

if (window.location.hostname === "localhost" && process.env.NODE_ENV === 'development') {
  console.log("Development mode: Connecting to Firebase Emulators...");
  try {
    connectAuthEmulator(auth, "http://localhost:9099");
    connectFirestoreEmulator(db, "localhost", 8081); // Port from firebase.json
    console.log("Successfully connected to Auth and Firestore Emulators.");
  } catch (error) {
    console.error("Error connecting to Firebase emulators:", error);
  }
}

export { auth, db };
```
*The `projectId` in `firebaseConfig` should be consistent, e.g., `"demo-ai-tutor"` or your actual Firebase project ID, when working with emulators to ensure different parts of your app (frontend, backend scripts) target the same emulated project.*

**Backend Agents (Python):**
Set the `FIRESTORE_EMULATOR_HOST` environment variable for Python services:
```bash
export FIRESTORE_EMULATOR_HOST="localhost:8081"
```
The `google-cloud-firestore` client library automatically detects this. The Firestore client in Python should also be initialized with the same `project_id` used by other services connecting to the emulator.

**For Pub/Sub Emulator (Python):**
Set the `PUBSUB_EMULATOR_HOST` environment variable:
```bash
export PUBSUB_EMULATOR_HOST="localhost:8085"
```

## 3. Vertex AI Setup (Conceptual)

For agents interacting with Vertex AI (Gemini):
1.  **Enable Vertex AI API:** In your Google Cloud project, ensure the "Vertex AI API" is enabled.
2.  **Authentication:**
    *   **Local Development:**
        *   Run `gcloud auth application-default login`.
        *   Alternatively, set `GOOGLE_APPLICATION_CREDENTIALS` to the path of a service account JSON key.
    *   **Cloud Run Deployment:** Use the runtime service account with the "Vertex AI User" role.
3.  **Environment Variables for Agents:**
    *   `VERTEX_PROJECT_ID`: Your Google Cloud Project ID.
    *   `VERTEX_LOCATION`: The region for Vertex AI services (e.g., "us-central1").

*(Further sections like Backend Setup, Frontend Setup will be added as we build those parts)*
