# Spelling Accuracy Test Backend

This backend service provides APIs for a spelling accuracy test feature that helps in detecting potential dyslexia in children.

## Features

- Age-group based word tests
- Image-based word prompts
- Interactive spelling interface
- Real-time scoring and accuracy calculation
- Dyslexia detection indicators
- Performance tracking

## Setup

1. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Initialize the database:
```bash
python init_db.py
```

4. Run the server:
```bash
uvicorn main:app --reload
```

## API Endpoints

### GET /words/{age_group}
Retrieves word tests for a specific age group.

### POST /submit-response
Submits a user's response for scoring and analysis.

## Environment Variables

Create a `.env` file with the following variables:
```
DATABASE_URL=sqlite:///./spelling_test.db
```

## Frontend Integration

The backend is configured to work with the frontend running on `http://localhost:3000`. Update the CORS settings in `main.py` if your frontend runs on a different port.

## Development

- Python 3.10
- FastAPI
- SQLAlchemy
- SQLite (can be configured to use other databases) 