import React, { useState, useEffect } from 'react';
import { 
  Box, 
  Typography, 
  Container, 
  Paper, 
  Button, 
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  CircularProgress
} from '@mui/material';
import axios from 'axios';

const AGE_GROUPS = ['5-7', '8-10', '11-13', '14+'];

const BACKEND_URL = 'http://localhost:8000';

const SpellingTest = () => {
  const [ageGroup, setAgeGroup] = useState('');
  const [words, setWords] = useState([]);
  const [currentWordIndex, setCurrentWordIndex] = useState(0);
  const [userInput, setUserInput] = useState('');
  const [startTime, setStartTime] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [testStarted, setTestStarted] = useState(false);

  const fetchWords = async (selectedAgeGroup) => {
    try {
      setLoading(true);
      const response = await axios.get(`${BACKEND_URL}/words/${selectedAgeGroup}`);
      setWords(response.data);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching words:', error);
      setLoading(false);
    }
  };

  const handleAgeGroupSelect = (event) => {
    const selectedAge = event.target.value;
    setAgeGroup(selectedAge);
    setTestStarted(false);
    setCurrentWordIndex(0);
    setResult(null);
    fetchWords(selectedAge);
  };

  const startTest = () => {
    setTestStarted(true);
    setStartTime(Date.now());
    setUserInput('');
    setResult(null);
  };

  const handleSubmit = async () => {
    if (!words[currentWordIndex]) return;

    const timeTaken = (Date.now() - startTime) / 1000; // Convert to seconds
    
    try {
      const response = await axios.post(`${BACKEND_URL}/submit-response`, {
        word_test_id: words[currentWordIndex].id,
        user_spelling: userInput,
        time_taken: timeTaken
      });

      setResult(response.data);

      // Move to next word after 3 seconds
      setTimeout(() => {
        if (currentWordIndex < words.length - 1) {
          setCurrentWordIndex(prev => prev + 1);
          setUserInput('');
          setStartTime(Date.now());
          setResult(null);
        } else {
          // Test completed
          setTestStarted(false);
        }
      }, 3000);

    } catch (error) {
      console.error('Error submitting response:', error);
    }
  };

  const getCurrentWord = () => words[currentWordIndex];

  const getImageUrl = (relativePath) => {
    return `${BACKEND_URL}${relativePath}`;
  };

  return (
    <Container maxWidth="md">
      <Box sx={{ my: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom align="center">
          Spelling Test
        </Typography>

        <Paper elevation={3} sx={{ p: 3, mb: 3 }}>
          <FormControl fullWidth sx={{ mb: 3 }}>
            <InputLabel>Select Age Group</InputLabel>
            <Select
              value={ageGroup}
              onChange={handleAgeGroupSelect}
              label="Select Age Group"
            >
              {AGE_GROUPS.map((age) => (
                <MenuItem key={age} value={age}>{age} years</MenuItem>
              ))}
            </Select>
          </FormControl>

          {loading ? (
            <Box display="flex" justifyContent="center">
              <CircularProgress />
            </Box>
          ) : words.length > 0 && !testStarted ? (
            <Box display="flex" justifyContent="center">
              <Button variant="contained" color="primary" onClick={startTest}>
                Start Test
              </Button>
            </Box>
          ) : null}

          {testStarted && getCurrentWord() && (
            <Box sx={{ textAlign: 'center' }}>
              <Box sx={{ mb: 3 }}>
                <img 
                  src={getImageUrl(getCurrentWord().image_url)} 
                  alt="Word to spell"
                  style={{ 
                    maxWidth: '200px', 
                    height: 'auto',
                    borderRadius: '8px',
                    boxShadow: '0 4px 8px rgba(0,0,0,0.1)'
                  }}
                />
              </Box>

              <Typography variant="h6" gutterBottom>
                Hint: {getCurrentWord().hint}
              </Typography>

              <TextField
                fullWidth
                label="Type the word"
                value={userInput}
                onChange={(e) => setUserInput(e.target.value)}
                sx={{ mb: 2 }}
              />

              <Button
                variant="contained"
                color="primary"
                onClick={handleSubmit}
                disabled={!userInput}
              >
                Submit
              </Button>
            </Box>
          )}

          {result && (
            <Box sx={{ mt: 3, textAlign: 'center' }}>
              <Typography variant="h6" color={result.accuracy > 0.8 ? 'success.main' : 'error.main'}>
                Score: {Math.round(result.score)}%
              </Typography>
              <Typography variant="body1">
                Accuracy: {Math.round(result.accuracy * 100)}%
              </Typography>
              {result.dyslexia_indicator > 0.3 && (
                <Typography variant="body2" color="warning.main" sx={{ mt: 1 }}>
                  Some spelling patterns suggest potential dyslexia indicators.
                  Consider consulting with an education specialist.
                </Typography>
              )}
            </Box>
          )}
        </Paper>
      </Box>
    </Container>
  );
};

export default SpellingTest; 