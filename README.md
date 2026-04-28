# HCPFiller - AI-Powered HCP Interaction Logger

## Overview
Production-ready scaffold with **FastAPI + LangGraph** backend and **React + Redux Toolkit + Tailwind CSS** frontend. The AI Assistant automates data entry by extracting HCP interaction details from natural language chat and populating the form in real-time.

---

## 🛠️ Quick Start (using Makefile)

This project includes a root-level `Makefile` to simplify setup and development.

### 1. Initial Setup
Run this command once to install all dependencies for both Backend and Frontend.
```powershell
make install
```
*   **What it does**: Creates a Python virtual environment, installs backend requirements, and runs `npm install` in the Frontend directory.

### 2. Database Initialization
Ensure your database is ready before starting the app.
```powershell
make db-init
```
*   **What it does**: Runs the database initialization script to create necessary tables.

### 3. Running the Application
Start both the backend and frontend concurrently.
```powershell
make dev
```
*   **When to use**: Use this for standard daily development. It opens two terminal windows running the FastAPI server and the Vite dev server.

### 4. Granular Commands
Run frontend backend one by one
*   **Backend Only**: `make dev-backend`
*   **Frontend Only**: `make dev-frontend`
*   **Clean Up**: `make clean` (Removes `__pycache__` and temporary files)

---

## 🧠 AI Features & Agent Tools

The AI Assistant is powered by a **LangGraph** agent that has access to a specialized suite of tools for managing HCP interactions.

### 🛠️ Available Agent Tools:

1.  **`upsert_form_draft`**: 
    *   **Purpose**: Extracts partial data from chat and populates the frontend form in real-time.
    *   **Behavior**: Creates a new session ID if none exists, or updates the current draft. It enables the "live-sync" feel between chat and form.

2.  **`save_interaction_to_db`**: 
    *   **Purpose**: Finalizes the interaction and saves it to the permanent database.
    *   **Behavior**: Triggered when the AI detects the user wants to "submit" or "finalize" the log. It ensures all mandatory fields are captured.

3.  **`list_recent_interactions`**: 
    *   **Purpose**: Retrieves the 10 most recent logs from the database.
    *   **Behavior**: Returns a formatted table in the chat, allowing users to quickly see their recent activity.

4.  **`load_interaction_detail`**: 
    *   **Purpose**: Pulls all fields of a specific historical interaction back into the form.
    *   **Behavior**: Used when a user says "Show me the details of the meeting with Dr. Smith" or provides a specific Interaction ID.

5.  **`search_interactions`**: 
    *   **Purpose**: Filters historical logs based on criteria like **Sentiment** or **Date**.
    *   **Behavior**: Helps users find specific past interactions (e.g., "Find all negative sentiment meetings from last week").

6.  **`analyze_sentiment_and_topics`**: 
    *   **Purpose**: An internal analysis tool that provides suggestions for the "Sentiment" and "Topics" fields based on the tone of the user's description.

---

### 🌟 Advanced AI Capabilities
*   **Persistent Context**: The AI remembers which interaction you are working on using `session_id`, allowing for multi-turn corrections.
*   **Automatic Upserts**: When the AI extracts data, it smartly updates existing records rather than creating duplicates.
*   **Table Rendering**: Data lists (like search results) are automatically rendered as clean, high-contrast tables in the chat window.

---

## 🏗️ Directory Structure

```
HCPFiller/
├── Backend/          ← FastAPI + LangGraph Agent
│   ├── app/
│   │   ├── agent/    ← LangGraph Logic & Tools
│   │   ├── api/      ← Endpoints (AI, Interactions, Health)
│   │   ├── models/   ← SQLModel Database Models
│   │   └── services/ ← AI Business Logic
├── Frontend/         ← React + Redux + Tailwind
│   ├── src/
│   │   ├── store/    ← Redux Toolkit Slices
│   │   ├── components/ ← Premium UI Components
│   │   └── api/      ← Backend API Integration
└── Makefile          ← Unified Project Commands
```

---

## 🛠️ Tech Stack
- **Backend**: FastAPI, LangGraph, SQLModel, Pydantic v2.
- **Frontend**: React, Redux Toolkit, Vite, Tailwind CSS (Pure Utilities).
- **AI**: Groq (Llama 3) for high-speed extraction.
- **Database**: SQLite (Development) / PostgreSQL (Production ready).
