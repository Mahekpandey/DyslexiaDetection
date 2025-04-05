import React, { useState, useEffect, useCallback, useRef } from 'react';
import axios from 'axios';
import styled from 'styled-components';
import { useNavigate } from 'react-router-dom';

const GameContainer = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 2rem;
  min-height: 100vh;
  background: #121212;
  color: white;
`;

const GameBoard = styled.div`
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1rem;
  max-width: 600px;
  margin: 2rem auto;
  padding: 2rem;
  background: #1E1E1E;
  border-radius: 12px;
  box-shadow: 0 4px 8px rgba(147, 112, 219, 0.2);
  border: 1px solid rgba(147, 112, 219, 0.3);
`;

const Hole = styled.div`
  width: 100px;
  height: 100px;
  background: #2A2A2A;
  border-radius: 50%;
  position: relative;
  overflow: hidden;
  cursor: pointer;
  box-shadow: inset 0 10px 20px rgba(0, 0, 0, 0.5),
              0 0 15px rgba(147, 112, 219, 0.2);
  border: 2px solid rgba(147, 112, 219, 0.2);
  transition: all 0.3s ease;

  &:hover {
    transform: scale(1.05);
    box-shadow: inset 0 10px 20px rgba(0, 0, 0, 0.5),
                0 0 20px rgba(147, 112, 219, 0.4);
  }
`;

const Character = styled.div`
  width: 90px;
  height: 90px;
  background: #673AB7;
  border-radius: 50%;
  position: absolute;
  top: ${props => props.isVisible ? '10%' : '100%'};
  left: 5%;
  transition: top 0.3s;
  cursor: pointer;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);

  &:hover {
    background: #7E57C2;
  }
`;

const GameInfo = styled.div`
  display: flex;
  justify-content: space-around;
  width: 100%;
  max-width: 600px;
  margin: 1rem 0;
  padding: 1.5rem;
  background: #1E1E1E;
  border-radius: 12px;
  box-shadow: 0 4px 8px rgba(147, 112, 219, 0.2);
  border: 1px solid rgba(147, 112, 219, 0.3);
  color: white;
  font-size: 1.2rem;

  div {
    display: flex;
    align-items: center;
    font-weight: bold;
    color: #B39DDB;
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
  border: 1px solid rgba(147, 112, 219, 0.3);

  &:hover {
    background: #7E57C2;
    transform: translateY(-2px);
    box-shadow: 0 4px 8px rgba(147, 112, 219, 0.3);
  }

  &:disabled {
    background: #4A4A4A;
    cursor: not-allowed;
    transform: none;
    box-shadow: none;
  }
`;

const WhackAMole = () => {
  const navigate = useNavigate();
  const [gameStarted, setGameStarted] = useState(false);
  const [activeHole, setActiveHole] = useState(null);
  const [attempts, setAttempts] = useState(0);
  const [currentAttemptStarted, setCurrentAttemptStarted] = useState(false);
  const [gameCompleted, setGameCompleted] = useState(false);
  const timeoutRef = useRef(null);
  const MAX_ATTEMPTS = 3;

  // Cleanup function
  useEffect(() => {
    return () => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }
    };
  }, []);

  const startGame = async () => {
    try {
      await axios.post('http://localhost:5000/api/whackamole/start');
      setGameStarted(true);
      setAttempts(0);
      setGameCompleted(false);
      showNextCharacter();
    } catch (error) {
      console.error('Error starting game:', error);
    }
  };

  const endGame = useCallback(async () => {
    try {
      setGameCompleted(true);
      setGameStarted(false);
      setActiveHole(null);
      setCurrentAttemptStarted(false);
      
      // Calculate final score before navigating
      await axios.post('http://localhost:5000/api/whackamole/calculate-score');
      navigate('/whackamole-results');
    } catch (error) {
      console.error('Error ending game:', error);
    }
  }, [navigate]);

  const showNextCharacter = useCallback(() => {
    if (attempts >= MAX_ATTEMPTS) {
      endGame();
      return;
    }

    // Clear any existing timeout
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
    }

    const nextHole = Math.floor(Math.random() * 9);
    setActiveHole(nextHole);
    setCurrentAttemptStarted(true);

    // Start timing the attempt
    axios.post('http://localhost:5000/api/whackamole/record-attempt')
      .catch(error => console.error('Error starting attempt:', error));

    // Hide character after random time (1-2 seconds)
    timeoutRef.current = setTimeout(() => {
      if (currentAttemptStarted) {
        // If not hit, record a miss
        handleMiss();
      }
    }, Math.random() * 1000 + 1000);
  }, [attempts, currentAttemptStarted, endGame]);

  const handleAttemptComplete = useCallback(async () => {
    try {
      await axios.post('http://localhost:5000/api/whackamole/end-attempt');
      const newAttempts = attempts + 1;
      setAttempts(newAttempts);
      setActiveHole(null);
      setCurrentAttemptStarted(false);

      // Clear the timeout to prevent duplicate misses
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
        timeoutRef.current = null;
      }

      if (newAttempts >= MAX_ATTEMPTS) {
        endGame();
      } else {
        // Show next character after a short delay
        setTimeout(showNextCharacter, 1000);
      }
    } catch (error) {
      console.error('Error completing attempt:', error);
    }
  }, [attempts, endGame, showNextCharacter]);

  const handleHit = async (holeIndex) => {
    if (!currentAttemptStarted || holeIndex !== activeHole || gameCompleted) return;
    await handleAttemptComplete();
  };

  const handleMiss = async () => {
    if (!currentAttemptStarted || gameCompleted) return;
    await handleAttemptComplete();
  };

  return (
    <GameContainer>
      <h1>Whack-A-Mole Response Time Test</h1>
      <GameInfo>
        <div>Attempts: {attempts}/{MAX_ATTEMPTS}</div>
        {!gameStarted && !gameCompleted && (
          <Button onClick={startGame}>Start Game</Button>
        )}
      </GameInfo>
      <GameBoard>
        {Array(9).fill(null).map((_, index) => (
          <Hole key={index} onClick={() => handleHit(index)}>
            <Character isVisible={activeHole === index} />
          </Hole>
        ))}
      </GameBoard>
      <p>Click on the character as soon as it appears!</p>
    </GameContainer>
  );
};

export default WhackAMole; 