Travel Planner API
This is a technical assessment for the Junior Python Developer position. The application allows users to plan trips by creating projects and adding places of interest, integrated with the Art Institute of Chicago's public collection.

Tech Stack
FastAPI — Modern, high-performance web framework.

SQLAlchemy + SQLite — ORM and Database (local file-based).

Pydantic — Data validation and settings management.

Art Institute of Chicago API — Third-party service integration.

HTTPX — Asynchronous HTTP client for API requests.

Key Features & Business Logic
Project Management: Full CRUD operations for travel plans.

Smart Validation:

Maximum 10 places per project.

Prevents duplicate places within the same project.

Real-time validation of external_id against the Chicago Art Institute API.

Deletion Rules: Projects cannot be deleted if at least one place has been marked as "visited".

Auto-completion: Projects are automatically marked as "completed" once all associated places are visited.

Performance: In-memory caching for third-party API responses to minimize external network calls.

How to Run Locally
Clone the repository:

Bash
git clone <your-repo-link>
cd travel_planner
Set up a virtual environment:

Bash
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
Install dependencies:

Bash
pip install -r requirements.txt
Start the server:

Bash
uvicorn main:app --reload
Access the API Documentation:
Open http://127.0.0.1:8000/docs in your browser to explore the Interactive Swagger UI.

Run with Docker
If you have Docker installed, you can launch the entire stack with a single command:

Bash
docker-compose up --build
The API will be available at http://localhost:8000.
