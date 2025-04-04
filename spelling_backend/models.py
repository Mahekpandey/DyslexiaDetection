from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class WordTest(Base):
    __tablename__ = "word_tests"

    id = Column(Integer, primary_key=True, index=True)
    word = Column(String, nullable=False)
    image_url = Column(String, nullable=False)
    hint = Column(String, nullable=False)
    age_group = Column(String, nullable=False)  # e.g., "5-7", "8-10", "11-13", "14+"
    difficulty_level = Column(Integer, nullable=False)  # 1 to 5
    responses = relationship("UserResponse", back_populates="word_test")

class UserResponse(Base):
    __tablename__ = "user_responses"

    id = Column(Integer, primary_key=True, index=True)
    word_test_id = Column(Integer, ForeignKey("word_tests.id"))
    user_spelling = Column(String, nullable=False)
    time_taken = Column(Float, nullable=False)  # Time taken in seconds
    score = Column(Float, nullable=False)  # Overall score (0-100)
    accuracy = Column(Float, nullable=False)  # Spelling accuracy (0-1)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    word_test = relationship("WordTest", back_populates="responses")

    # Fields for dyslexia detection analysis
    letter_reversals = Column(Integer, default=0)  # Count of reversed letters (b/d, p/q)
    phonetic_errors = Column(Integer, default=0)  # Count of phonetic-based mistakes
    sequence_errors = Column(Integer, default=0)  # Count of letter sequence mistakes
    dyslexia_indicator = Column(Float, nullable=False)  # Calculated indicator (0-1) 