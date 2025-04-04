from database import engine, SessionLocal
from models import Base, WordTest

def init_db():
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    # Sample word tests for different age groups
    sample_words = [
        # Age group 5-7 (Level 1)
        {
            "word": "cat",
            "image_url": "/static/images/cat.jpg",
            "hint": "A small furry pet that says meow",
            "age_group": "5-7",
            "difficulty_level": 1
        },
        {
            "word": "dog",
            "image_url": "/static/images/dog.jpg",
            "hint": "A friendly pet that barks",
            "age_group": "5-7",
            "difficulty_level": 1
        },
        # Age group 8-10 (Level 2)
        {
            "word": "elephant",
            "image_url": "/static/images/elephant.jpg",
            "hint": "A large gray animal with a trunk",
            "age_group": "8-10",
            "difficulty_level": 2
        },
        {
            "word": "giraffe",
            "image_url": "/static/images/giraffe.jpg",
            "hint": "A tall animal with a long neck",
            "age_group": "8-10",
            "difficulty_level": 2
        },
        # Age group 11-13 (Level 3)
        {
            "word": "beautiful",
            "image_url": "/static/images/beautiful.jpg",
            "hint": "Looking very pretty or attractive",
            "age_group": "11-13",
            "difficulty_level": 3
        },
        {
            "word": "knowledge",
            "image_url": "/static/images/knowledge.jpg",
            "hint": "Information and skills gained through learning",
            "age_group": "11-13",
            "difficulty_level": 3
        },
        # Age group 14+ (Level 4)
        {
            "word": "psychology",
            "image_url": "/static/images/psychology.jpg",
            "hint": "The study of mind and behavior",
            "age_group": "14+",
            "difficulty_level": 4
        },
        {
            "word": "phenomenon",
            "image_url": "/static/images/phenomenon.jpg",
            "hint": "A remarkable or unusual occurrence",
            "age_group": "14+",
            "difficulty_level": 4
        }
    ]
    
    # Create database session
    db = SessionLocal()
    try:
        # Delete all existing words to ensure clean state
        db.query(WordTest).delete()
        db.commit()
        
        # Add sample words
        for word_data in sample_words:
            word_test = WordTest(**word_data)
            db.add(word_test)
        db.commit()
        print("Database initialized with sample word tests.")
    finally:
        db.close()

if __name__ == "__main__":
    init_db()