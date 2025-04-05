import React, { useState, useEffect } from 'react';
import axios from 'axios';
import styled from 'styled-components';
import { useNavigate } from 'react-router-dom';

const ResultsContainer = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 2rem;
  min-height: 100vh;
  background: #121212;
  color: white;
`;

const ResultsCard = styled.div`
  background: #1E1E1E;
  padding: 2rem;
  border-radius: 12px;
  box-shadow: 0 4px 8px rgba(147, 112, 219, 0.2);
  max-width: 600px;
  width: 100%;
  margin: 2rem 0;
  border: 1px solid rgba(147, 112, 219, 0.3);
`;

const ResultsList = styled.div`
  margin: 2rem 0;
  width: 100%;
`;

const ResultItem = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  border-bottom: 1px solid rgba(147, 112, 219, 0.2);
  font-size: 1.1rem;
  color: white;
  
  &:last-child {
    border-bottom: none;
  }

  .attempt-score {
    color: ${props => {
      if (props.score >= 90) return '#B39DDB';
      if (props.score >= 75) return '#9575CD';
      if (props.score >= 60) return '#7E57C2';
      return '#673AB7';
    }};
    font-weight: bold;
  }
`;

const ScoreDisplay = styled.div`
  text-align: center;
  margin: 2rem 0;
  padding: 1.5rem;
  background: ${props => {
    if (props.score >= 90) return 'rgba(147, 112, 219, 0.2)';
    if (props.score >= 75) return 'rgba(147, 112, 219, 0.15)';
    if (props.score >= 60) return 'rgba(147, 112, 219, 0.1)';
    return 'rgba(147, 112, 219, 0.05)';
  }};
  border-radius: 12px;
  border: 1px solid rgba(147, 112, 219, 0.3);
  
  h3 {
    color: white;
    margin-bottom: 1rem;
    font-size: 1.5rem;
  }
  
  .score {
    font-size: 3.5rem;
    font-weight: bold;
    color: ${props => {
      if (props.score >= 90) return '#B39DDB';
      if (props.score >= 75) return '#9575CD';
      if (props.score >= 60) return '#7E57C2';
      return '#673AB7';
    }};
    margin: 1rem 0;
  }
`;

const Analysis = styled.div`
  margin: 2rem 0;
  padding: 1.5rem;
  background: ${props => {
    if (props.score >= 90) return 'rgba(147, 112, 219, 0.2)';
    if (props.score >= 75) return 'rgba(147, 112, 219, 0.15)';
    if (props.score >= 60) return 'rgba(147, 112, 219, 0.1)';
    return 'rgba(147, 112, 219, 0.05)';
  }};
  border-radius: 12px;
  text-align: center;
  border: 1px solid rgba(147, 112, 219, 0.3);
  
  h3 {
    color: white;
    margin-bottom: 1rem;
    font-size: 1.5rem;
  }
  
  .message {
    font-size: 1.8rem;
    font-weight: bold;
    margin-bottom: 1rem;
    color: ${props => {
      if (props.score >= 90) return '#B39DDB';
      if (props.score >= 75) return '#9575CD';
      if (props.score >= 60) return '#7E57C2';
      return '#673AB7';
    }};
  }
  
  .detail {
    font-size: 1.2rem;
    margin-bottom: 1rem;
    color: #E0E0E0;
  }
  
  .motivation {
    font-size: 1.3rem;
    font-weight: 500;
    color: ${props => {
      if (props.score >= 90) return '#B39DDB';
      if (props.score >= 75) return '#9575CD';
      if (props.score >= 60) return '#7E57C2';
      return '#673AB7';
    }};
  }
`;

const Button = styled.button`
  padding: 1rem 2rem;
  font-size: 1.2rem;
  background: #673AB7;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  margin-top: 2rem;
  border: 1px solid rgba(147, 112, 219, 0.3);

  &:hover {
    background: #7E57C2;
    transform: translateY(-2px);
    box-shadow: 0 4px 8px rgba(147, 112, 219, 0.3);
  }
`;

const LoadingContainer = styled(ResultsContainer)`
  justify-content: center;
  h1 {
    color: white;
    margin-bottom: 2rem;
  }
`;

const LoadingSpinner = styled.div`
  border: 4px solid #1E1E1E;
  border-top: 4px solid #673AB7;
  border-radius: 50%;
  width: 40px;
  height: 40px;
  animation: spin 1s linear infinite;
  margin: 2rem 0;

  @keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
  }
`;

const WhackAMoleResults = () => {
  const navigate = useNavigate();
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [retryCount, setRetryCount] = useState(0);

  useEffect(() => {
    const fetchResults = async () => {
      try {
        const response = await axios.get('http://localhost:5000/api/whackamole/results');
        if (response.data.status === 'success' && response.data.attempts && response.data.attempts.length > 0) {
          setResults(response.data);
          setLoading(false);
        } else if (retryCount < 3) {
          // If no results yet, retry after a short delay
          setTimeout(() => setRetryCount(prev => prev + 1), 1000);
        } else {
          setError('No results available. Please try the test again.');
          setLoading(false);
        }
      } catch (err) {
        console.error('Error fetching results:', err);
        if (retryCount < 3) {
          // Retry on error
          setTimeout(() => setRetryCount(prev => prev + 1), 1000);
        } else {
          setError('Failed to fetch results. Please try again.');
          setLoading(false);
        }
      }
    };

    fetchResults();
  }, [retryCount]);

  const handlePlayAgain = () => {
    navigate('/whackamole');
  };

  if (loading) {
    return (
      <LoadingContainer>
        <h1>Loading Results...</h1>
        <LoadingSpinner />
        <p>Processing your response times...</p>
      </LoadingContainer>
    );
  }

  if (error) {
    return (
      <ResultsContainer>
        <ResultsCard>
          <h2>Error</h2>
          <p>{error}</p>
          <Button onClick={handlePlayAgain}>Try Again</Button>
        </ResultsCard>
      </ResultsContainer>
    );
  }

  if (!results || !results.attempts || results.attempts.length === 0) {
    return (
      <ResultsContainer>
        <ResultsCard>
          <h2>No Results Available</h2>
          <p>Please complete the Whack-A-Mole test to see your results.</p>
          <Button onClick={handlePlayAgain}>Start Test</Button>
        </ResultsCard>
      </ResultsContainer>
    );
  }

  return (
    <ResultsContainer>
      <h1>Whack-A-Mole Test Results</h1>
      <ResultsCard>
        {results && (
          <>
            <ScoreDisplay score={results.score}>
              <h3>Your Score</h3>
              <div className="score">{results.score.toFixed(0)}%</div>
            </ScoreDisplay>

            <Analysis score={results.score}>
              <div className="message">{results.analysis.message}</div>
              <div className="detail">{results.analysis.detail}</div>
              <div className="motivation">{results.analysis.motivation}</div>
            </Analysis>

            <h2>Response Times</h2>
            <ResultsList>
              {results.attempts.map((attempt, index) => (
                <ResultItem key={index} score={attempt.score}>
                  <span>Attempt {index + 1}:</span>
                  <div>
                    <span>{attempt.response_time.toFixed(3)} seconds </span>
                    <span className="attempt-score">
                      (Score: {attempt.score.toFixed(0)}%)
                    </span>
                  </div>
                </ResultItem>
              ))}
              <ResultItem score={results.score} style={{ fontWeight: 'bold', marginTop: '1rem' }}>
                <span>Average Response Time:</span>
                <span>{results.average_response_time.toFixed(3)} seconds</span>
              </ResultItem>
            </ResultsList>

            <Button onClick={handlePlayAgain}>Play Again</Button>
          </>
        )}
      </ResultsCard>
    </ResultsContainer>
  );
};

export default WhackAMoleResults; 