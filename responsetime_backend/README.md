# Whack-a-Mole Response Time Game Backend

This is the backend service for the Whack-a-Mole response time game, designed to measure cognitive response times in children as part of dyslexia assessment.

## Game Overview

The Whack-a-Mole game is a cognitive assessment tool that measures:
- Visual Processing Speed
- Hand-Eye Coordination
- Response Time Accuracy
- Sustained Attention

### Game Mechanics

1. **Game Flow**:
   - Each session consists of 3 attempts
   - For each attempt, a character appears randomly in one of 9 holes
   - The character remains visible for 1-2 seconds
   - Players must click the character as quickly as possible
   - Response times are recorded for each attempt

2. **Timing System**:
   - Start time is recorded when character appears
   - End time is recorded when player clicks
   - Response time = End time - Start time
   - Maximum response window: 2000ms (2 seconds)

3. **Scoring Formula**:
   ```
   Individual Attempt Score = (2000 - response_time_ms) / 2000 * 100
   Final Score = Average of all 3 attempts
   ```

4. **Performance Categories**:
   - Champion (≥90%): Exceptional response time
   - Great (≥75%): Above average response time
   - Good (≥60%): Normal response time
   - Learning (<60%): Below average response time

## Technical Implementation

### Frontend Integration
- Built with React
- Styled using styled-components
- Dark theme with purple accents for better visibility
- Responsive design for various screen sizes

### Backend Architecture

1. **Session Management**:
   ```python
   {
       'session_id': {
           'attempts': [],
           'start_times': [],
           'end_times': [],
           'scores': []
       }
   }
   ```

2. **Response Time Calculation**:
   ```python
   response_time = end_time - start_time
   attempt_score = ((2000 - response_time) / 2000) * 100
   ```

3. **Score Analysis**:
   - Mean response time
   - Standard deviation
   - Consistency across attempts
   - Outlier detection

## Setup

1. Ensure you have Python 3.10 installed
2. Create and activate virtual environment:
   ```bash
   python -m venv venv
   # On Windows
   .\venv\Scripts\activate
   # On Unix/MacOS
   source venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Running the Server

1. Activate the virtual environment (if not already activated)
2. Run the Flask application:
   ```bash
   python app.py
   ```
3. The server will start on http://localhost:5000

## API Endpoints

### Game Flow Endpoints

1. `POST /api/whackamole/start`
   - Initializes a new game session
   - Returns: `{ "session_id": string }`

2. `POST /api/whackamole/record-attempt`
   - Records the start time of an attempt
   - Updates session state
   - No request body needed

3. `POST /api/whackamole/end-attempt`
   - Records the end time of an attempt
   - Calculates attempt score
   - No request body needed

4. `POST /api/whackamole/calculate-score`
   - Calculates final score and performance metrics
   - Returns:
     ```json
     {
       "final_score": number,
       "attempts": [number, number, number],
       "category": string,
       "feedback": string
     }
     ```

## Environment Variables

Create a `.env` file with the following variables:
```
SECRET_KEY=your-secret-key-here
FLASK_ENV=development
FLASK_APP=app.py
```

## Performance Metrics

The system analyzes several key metrics:

1. **Response Time**:
   - Raw response time in milliseconds
   - Normalized score (0-100)
   - Consistency between attempts

2. **Accuracy**:
   - Successful hits vs misses
   - Early/late response patterns
   - Response precision

3. **Pattern Analysis**:
   - Learning curve across attempts
   - Fatigue indicators
   - Attention span metrics

## Educational Impact

The Whack-a-Mole game serves as:
1. A diagnostic tool for cognitive processing speed
2. An early indicator of potential learning difficulties
3. A fun and engaging way to assess children
4. A quantitative measure for tracking progress

## References

1. Response time measurement methodology based on cognitive psychology research
2. Scoring system adapted from standardized cognitive assessment tools
3. Game design informed by educational psychology principles 