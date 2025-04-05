import React, { useState, useEffect, useCallback, useRef } from 'react';
import axios from 'axios';
import styled from 'styled-components';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';

const MAX_ATTEMPTS = 3;
const SHOW_DURATION = 1000;

const GameContainer = styled.div`
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

const GameInfo = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
  margin-bottom: 2rem;
  color: white;
  font-size: 1.5rem;
  z-index: 10;
`;

const GameBoard = styled.div`
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1rem;
  padding: 2rem;
  background: rgba(26, 26, 26, 0.8);
  backdrop-filter: blur(10px);
  border-radius: 20px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  box-shadow: 0 8px 32px rgba(156, 39, 176, 0.2);
  z-index: 10;
`;

const Hole = styled.div`
  width: 100px;
  height: 100px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.05);
  border: 2px solid rgba(156, 39, 176, 0.3);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s ease;

  &:hover {
    transform: scale(1.05);
    border-color: rgba(156, 39, 176, 0.5);
  }
`;

const Character = styled.div`
  width: 80%;
  height: 80%;
  border-radius: 50%;
  background: ${props => props.isVisible ? 'linear-gradient(45deg, #9C27B0 30%, #E040FB 90%)' : 'transparent'};
  opacity: ${props => props.isVisible ? 1 : 0};
  transition: all 0.2s ease;
  box-shadow: ${props => props.isVisible ? '0 3px 20px rgba(156, 39, 176, 0.3)' : 'none'};
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

const WhackAMole = () => {
  const navigate = useNavigate();
  const [gameStarted, setGameStarted] = useState(false);
  const [activeHole, setActiveHole] = useState(null);
  const [attempts, setAttempts] = useState(0);
  const [currentAttemptStarted, setCurrentAttemptStarted] = useState(false);
  const [gameCompleted, setGameCompleted] = useState(false);
  const timeoutRef = useRef(null);

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
      <p style={{ color: 'white', marginTop: '2rem', zIndex: 10 }}>Click on the character as soon as it appears!</p>

      <div className="absolute inset-0 bg-gradient-to-t from-[#030303] via-transparent to-[#030303]/80 pointer-events-none" />
    </GameContainer>
  );
};

export default WhackAMole; 