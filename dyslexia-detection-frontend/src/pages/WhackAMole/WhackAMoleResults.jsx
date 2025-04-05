import React, { useState, useEffect } from 'react';
import axios from 'axios';
import styled from 'styled-components';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';

const ResultsContainer = styled.div`
  min-height: 100vh;
  width: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding-top: 150px;
  position: relative;
  overflow: hidden;
  background: #030303;

  h1 {
    color: white;
    margin-bottom: 2rem;
    font-size: 2.5rem;
    text-align: center;
    z-index: 10;
  }
`;

const ResultsCard = styled.div`
  padding: 2rem;
  width: 90%;
  max-width: 800px;
  background: rgba(26, 26, 26, 0.8);
  backdrop-filter: blur(10px);
  border-radius: 20px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  box-shadow: 0 8px 32px rgba(156, 39, 176, 0.2);
  color: white;
  z-index: 10;
`;

const ResultsList = styled.div`
  margin: 2rem 0;
  display: flex;
  flex-direction: column;
  gap: 1rem;
`;

const ResultItem = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  color: white;

  .attempt-score {
    color: ${props => {
      if (props.score >= 90) return '#E040FB';
      if (props.score >= 75) return '#D500F9';
      if (props.score >= 60) return '#AA00FF';
      return '#9C27B0';
    }};
    margin-left: 1rem;
  }
`;

const ScoreDisplay = styled.div`
  text-align: center;
  margin-bottom: 2rem;
  padding: 2rem;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 16px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);

  h3 {
    color: white;
    margin-bottom: 1rem;
    font-size: 1.5rem;
  }

  .score {
    font-size: 4rem;
    font-weight: bold;
    background: linear-gradient(45deg, #9C27B0 30%, #E040FB 90%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
  }
`;

const Analysis = styled.div`
  margin: 2rem 0;
  padding: 1.5rem;
  background: rgba(156, 39, 176, 0.1);
  border-radius: 12px;
  text-align: center;
  border: 1px solid rgba(156, 39, 176, 0.2);
  
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
      if (props.score >= 90) return '#E040FB';
      if (props.score >= 75) return '#D500F9';
      if (props.score >= 60) return '#AA00FF';
      return '#9C27B0';
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
      if (props.score >= 90) return '#E040FB';
      if (props.score >= 75) return '#D500F9';
      if (props.score >= 60) return '#AA00FF';
      return '#9C27B0';
    }};
  }
`;

const Button = styled.button`
  padding: 1rem 2rem;
  font-size: 1.2rem;
  background: linear-gradient(45deg, #9C27B0 30%, #E040FB 90%);
  color: white;
  border: none;
  border-radius: 50px;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 3px 20px rgba(156, 39, 176, 0.3);

  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 5px 25px rgba(156, 39, 176, 0.5);
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
  border: 4px solid rgba(156, 39, 176, 0.1);
  border-top: 4px solid #9C27B0;
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

function ElegantShape({
  className,
  delay = 0,
  width = 400,
  height = 100,
  rotate = 0,
  gradient = "from-white/[0.08]",
}) {
  return (
    <motion.div
      initial={{
        opacity: 0,
        y: -150,
        rotate: rotate - 15,
      }}
      animate={{
        opacity: 1,
        y: 0,
        rotate: rotate,
      }}
      transition={{
        duration: 2.4,
        delay,
        ease: [0.23, 0.86, 0.39, 0.96],
        opacity: { duration: 1.2 },
      }}
      className={`absolute ${className}`}
    >
      <motion.div
        animate={{
          y: [0, 15, 0],
        }}
        transition={{
          duration: 12,
          repeat: Number.POSITIVE_INFINITY,
          ease: "easeInOut",
        }}
        style={{
          width,
          height,
        }}
        className="relative"
      >
        <div
          className={`absolute inset-0 rounded-full bg-gradient-to-r to-transparent ${gradient} backdrop-blur-[2px] border-2 border-white/[0.15] shadow-[0_8px_32px_0_rgba(255,255,255,0.1)] after:absolute after:inset-0 after:rounded-full after:bg-[radial-gradient(circle_at_50%_50%,rgba(255,255,255,0.2),transparent_70%)]`}
        />
      </motion.div>
    </motion.div>
  );
}

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
        <div className="absolute inset-0 bg-gradient-to-br from-purple-500/[0.05] via-transparent to-rose-500/[0.05] blur-3xl" />
        <h1>Loading Results...</h1>
        <LoadingSpinner />
        <p style={{ color: 'white', zIndex: 10 }}>Processing your response times...</p>
        <div className="absolute inset-0 bg-gradient-to-t from-[#030303] via-transparent to-[#030303]/80 pointer-events-none" />
      </LoadingContainer>
    );
  }

  if (error) {
    return (
      <ResultsContainer>
        <div className="absolute inset-0 bg-gradient-to-br from-purple-500/[0.05] via-transparent to-rose-500/[0.05] blur-3xl" />
        <ResultsCard>
          <h2>Error</h2>
          <p>{error}</p>
          <Button onClick={handlePlayAgain}>Try Again</Button>
        </ResultsCard>
        <div className="absolute inset-0 bg-gradient-to-t from-[#030303] via-transparent to-[#030303]/80 pointer-events-none" />
      </ResultsContainer>
    );
  }

  if (!results || !results.attempts || results.attempts.length === 0) {
    return (
      <ResultsContainer>
        <div className="absolute inset-0 bg-gradient-to-br from-purple-500/[0.05] via-transparent to-rose-500/[0.05] blur-3xl" />
        <ResultsCard>
          <h2>No Results Available</h2>
          <p>Please complete the Whack-A-Mole test to see your results.</p>
          <Button onClick={handlePlayAgain}>Start Test</Button>
        </ResultsCard>
        <div className="absolute inset-0 bg-gradient-to-t from-[#030303] via-transparent to-[#030303]/80 pointer-events-none" />
      </ResultsContainer>
    );
  }

  return (
    <ResultsContainer>
      <div className="absolute inset-0 bg-gradient-to-br from-purple-500/[0.05] via-transparent to-rose-500/[0.05] blur-3xl" />

      <div className="absolute inset-0 overflow-hidden">
        <ElegantShape
          delay={0.3}
          width={600}
          height={140}
          rotate={12}
          gradient="from-purple-500/[0.15]"
          className="left-[-10%] md:left-[-5%] top-[15%] md:top-[20%]"
        />

        <ElegantShape
          delay={0.5}
          width={500}
          height={120}
          rotate={-15}
          gradient="from-rose-500/[0.15]"
          className="right-[-5%] md:right-[0%] top-[70%] md:top-[75%]"
        />

        <ElegantShape
          delay={0.4}
          width={300}
          height={80}
          rotate={-8}
          gradient="from-violet-500/[0.15]"
          className="left-[5%] md:left-[10%] bottom-[5%] md:bottom-[10%]"
        />

        <ElegantShape
          delay={0.6}
          width={200}
          height={60}
          rotate={20}
          gradient="from-amber-500/[0.15]"
          className="right-[15%] md:right-[20%] top-[10%] md:top-[15%]"
        />
      </div>

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

      <div className="absolute inset-0 bg-gradient-to-t from-[#030303] via-transparent to-[#030303]/80 pointer-events-none" />
    </ResultsContainer>
  );
};

export default WhackAMoleResults; 