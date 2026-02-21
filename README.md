# 📄 Enterprise AI Document Assistant (RAG)

A fully containerized, asynchronous Retrieval-Augmented Generation (RAG) architecture designed to securely ingest, vectorize, and query PDF documents using local machine learning models. 

## 🏗️ System Architecture

This project is built with a microservices approach, completely isolated via Docker, ensuring reliable cross-container networking and resource management.

* **Frontend:** Streamlit (Provides a session-managed, interactive UI for document upload and querying).
* **Backend API:** FastAPI (Fully async, handling JWT authentication, rate limiting, and request routing).
* **Vector Database:** ChromaDB (Stores high-dimensional document embeddings for semantic search).
* **Relational Database:** PostgreSQL (Manages user state, RBAC, and access credentials).
* **Caching & Queues:** Redis + ARQ (Handles background tasks to prevent main-thread blocking during heavy document ingestion).
* **Infrastructure:** Docker & Docker Compose (Containerizes the entire stack with isolated networks and persistent volumes).

## 🚀 Core Features
* **Secure Document Ingestion:** Uploads PDFs directly to the FastAPI backend, where LangChain chunks and vectorizes the text into ChromaDB.
* **Context-Aware Querying:** Retrieves the most mathematically relevant document chunks to synthesize accurate, grounded answers.
* **JWT Authentication:** Protects the AI endpoints. The Streamlit frontend securely manages the token lifecycle to authenticate API calls.

## 🛠️ Engineering Challenges & Solutions

Building a multi-container AI system locally presented significant hardware constraints:
1. **WSL Stack Overflow & Memory Management:** The heavy load of running PostgreSQL, Redis, and vector processing caused Windows Subsystem for Linux (WSL) crashes. Resolved by manually clearing corrupted `backend.sock` networking loops and executing hard reboots of the Linux kernel.
2. **Storage Orchestration:** Docker image caching and volume expansion completely exhausted host system storage. Mitigated by implementing aggressive container pruning strategies (`docker system prune -a --volumes`) and carefully managing persistent volume mounts for the databases.
3. **Cross-Container Authorization:** Ensuring the Streamlit container could seamlessly pass Bearer tokens to the FastAPI container over the internal Docker network without triggering CORS or `401 Unauthorized` blocks.

## 💻 Quickstart (Local Deployment)

### Prerequisites
* Docker Engine & Docker Compose
* Python 3.10+ (for local UI testing)

### Booting the Engine
1. Clone the repository and navigate to the project directory.
2. Spin up the backend infrastructure (FastAPI, Postgres, Redis):
bash
docker compose up -d

3. Create the initial admin user to access the AI features:
Bash
docker compose run --rm create_superuser

### Launching the Dashboard
1. Install the frontend dependencies on your host machine:
Bash
pip install streamlit requests

2. Launch the UI:
Bash
streamlit run src/frontend.py

Open http://localhost:8501, log in with your admin credentials, and begin ingesting documents.