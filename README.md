# PersonaChat Backend API

A FastAPI backend for the PersonaChat application that provides AI character conversations using Google's Gemini API.

## Features

- Character-based AI responses using the Gemini API
- Response streaming for real-time chat experience
- Token usage tracking
- CORS support for frontend integration
- Containerized with Docker for easy deployment

## Tech Stack

- Python 3.11+
- FastAPI
- Uvicorn (ASGI server)
- Google Generative AI SDK
- Docker

## Local Development

### Prerequisites

- Python 3.11+
- Docker (optional, for containerization)

### Installation

1. Clone the repository:

```bash
git clone https://github.com/yourusername/personachat-backend.git
cd personachat-backend
```

2. Create a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Create a `.env` file with your Gemini API key:

```
GEMINI_API=your_gemini_api_key_here
```

5. Start the development server:

```bash
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`.

## API Endpoints

- `GET /`: Health check endpoint
- `POST /api/gemini-stream`: Main endpoint for streaming AI responses
  - Request body:
    ```json
    {
      "prompt": "Your message here",
      "character_name": "Character name (optional)"
    }
    ```

## Docker Deployment

### Building and Running Locally with Docker

1. Build the Docker image:

```bash
docker build -t personachat-api .
```

2. Run the container locally:

```bash
docker run -p 8000:8080 -e GEMINI_API=your_gemini_api_key_here personachat-api
```

The API will be available at `http://localhost:8000`.

### Deploying to Google Cloud Run

#### Prerequisites

- Google Cloud account
- Google Cloud SDK installed and configured

#### Deployment Steps

1. Enable required Google Cloud services:

```bash
gcloud services enable run.googleapis.com
gcloud services enable containerregistry.googleapis.com
```

2. Configure Docker for Google Cloud:

```bash
gcloud auth configure-docker
```

3. Tag your Docker image for Google Container Registry:

```bash
docker tag personachat-api gcr.io/your-project-id/personachat-api
```

4. Push the image to Google Container Registry:

```bash
docker push gcr.io/your-project-id/personachat-api
```

5. Deploy to Google Cloud Run:

```bash
gcloud run deploy personachat-api \
  --image gcr.io/your-project-id/personachat-api \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars="GEMINI_API=your_gemini_api_key_here"
```

6. After deployment, you'll receive a URL for your API.

7. Limit maximum instances (optional but recommended to control costs):

```bash
gcloud run services update personachat-api \
  --region=us-central1 \
  --max-instances=2
```

### CORS Configuration

If your frontend is hosted on a different domain, update the CORS settings in `main.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-frontend-domain.com"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Project Structure

```
backend/
├── main.py               # Main application entry point
├── requirements.txt      # Python dependencies
├── Dockerfile            # Docker configuration
├── .dockerignore         # Files to exclude from Docker builds
├── routers/              # API route definitions
│   ├── ai_routes.py      # AI-related endpoints
└── utils/                # Utility modules
    └── gemini_utils.py   # Gemini API utilities
```

## Notes on Google Cloud Run

- The service automatically scales to zero when not in use (no traffic)
- Default free tier includes 2 million requests/month and significant compute time
- Setting max instances helps control costs
- The `--allow-unauthenticated` flag makes your API publicly accessible

## Troubleshooting

- **Deployment issues**: Check Cloud Run logs in the Google Cloud Console
- **Container not starting**: Ensure your app listens on the port specified by the `PORT` environment variable
- **CORS errors**: Verify your CORS settings include your frontend domain
