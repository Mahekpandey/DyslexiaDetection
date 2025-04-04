from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from typing import List
import models
from database import engine, get_db
from pydantic import BaseModel
from datetime import datetime
import difflib
import os
from pathlib import Path

# Create database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Spelling Test API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update this with your frontend URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static directory for both paths
static_path = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=str(static_path)), name="static")
app.mount("/images", StaticFiles(directory=str(static_path / "images")), name="images")

# Pydantic models for request/response
class WordTestBase(BaseModel):
    word: str
    image_url: str
    hint: str
    age_group: str
    difficulty_level: int

class WordTestResponse(WordTestBase):
    id: int

    class Config:
        orm_mode = True

class UserResponseCreate(BaseModel):
    word_test_id: int
    user_spelling: str
    time_taken: float

class SpellingResult(BaseModel):
    score: float
    accuracy: float
    dyslexia_indicator: float
    letter_reversals: int
    phonetic_errors: int
    sequence_errors: int

# Helper functions
def analyze_spelling(expected: str, actual: str) -> dict:
    """Analyze spelling errors and calculate metrics"""
    # Calculate basic accuracy using sequence matcher
    accuracy = difflib.SequenceMatcher(None, expected.lower(), actual.lower()).ratio()
    
    # Initialize error counters
    letter_reversals = 0
    phonetic_errors = 0
    sequence_errors = 0
    
    # Common letter reversals
    reversal_pairs = [('b', 'd'), ('p', 'q'), ('m', 'w')]
    
    # Check for letter reversals
    for c1, c2 in reversal_pairs:
        if (c1 in expected and c2 in actual) or (c2 in expected and c1 in actual):
            letter_reversals += 1
    
    # Check for sequence errors (adjacent letter swaps)
    for i in range(len(expected) - 1):
        if i + 1 < len(actual):
            if expected[i:i+2] != actual[i:i+2] and set(expected[i:i+2]) == set(actual[i:i+2]):
                sequence_errors += 1
    
    # Calculate dyslexia indicator
    # Weight different factors in the indicator
    dyslexia_indicator = (
        (1 - accuracy) * 0.4 +
        (letter_reversals * 0.3) +
        (sequence_errors * 0.3)
    )
    dyslexia_indicator = min(1.0, dyslexia_indicator)
    
    # Calculate overall score (0-100)
    score = accuracy * 100
    
    return {
        "score": score,
        "accuracy": accuracy,
        "dyslexia_indicator": dyslexia_indicator,
        "letter_reversals": letter_reversals,
        "phonetic_errors": phonetic_errors,
        "sequence_errors": sequence_errors
    }

# API Endpoints
@app.get("/")
def read_root():
    return {"message": "Welcome to Spelling Test API"}

@app.get("/words/{age_group}", response_model=List[WordTestResponse])
def get_words_by_age(age_group: str, db: Session = Depends(get_db)):
    words = db.query(models.WordTest).filter(models.WordTest.age_group == age_group).all()
    if not words:
        raise HTTPException(status_code=404, detail=f"No words found for age group {age_group}")
    return words

@app.post("/submit-response", response_model=SpellingResult)
def submit_response(response: UserResponseCreate, db: Session = Depends(get_db)):
    # Get the word test
    word_test = db.query(models.WordTest).filter(models.WordTest.id == response.word_test_id).first()
    if not word_test:
        raise HTTPException(status_code=404, detail="Word test not found")
    
    # Analyze the spelling
    analysis = analyze_spelling(word_test.word, response.user_spelling)
    
    # Create user response record
    db_response = models.UserResponse(
        word_test_id=response.word_test_id,
        user_spelling=response.user_spelling,
        time_taken=response.time_taken,
        score=analysis["score"],
        accuracy=analysis["accuracy"],
        letter_reversals=analysis["letter_reversals"],
        phonetic_errors=analysis["phonetic_errors"],
        sequence_errors=analysis["sequence_errors"],
        dyslexia_indicator=analysis["dyslexia_indicator"]
    )
    
    db.add(db_response)
    db.commit()
    
    return SpellingResult(**analysis)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 