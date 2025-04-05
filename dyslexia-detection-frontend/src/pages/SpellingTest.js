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
  CircularProgress,
  Fade
} from '@mui/material';
import { styled, keyframes } from '@mui/material/styles';
import axios from 'axios';
import { motion } from 'framer-motion';

const AGE_GROUPS = ['5-7', '8-10', '11-13', '14+'];

const BACKEND_URL = 'http://localhost:8000';

const float = keyframes`
  0% { transform: translateY(0px); }
  50% { transform: translateY(-10px); }
  100% { transform: translateY(0px); }
`;

const StyledContainer = styled(Container)(({ theme }) => ({
  position: 'relative',
  zIndex: 10,
  paddingTop: '150px',
  '& .MuiTypography-h3': {
    marginBottom: theme.spacing(4),
    textAlign: 'center',
    animation: `${float} 3s ease-in-out infinite`,
  },
}));

const StyledPaper = styled(Paper)(({ theme }) => ({
  padding: theme.spacing(4),
  maxWidth: '800px',
  margin: '0 auto',
  backgroundColor: 'rgba(26, 26, 26, 0.8)',
  backdropFilter: 'blur(10px)',
  borderRadius: '20px',
  border: '1px solid rgba(255, 255, 255, 0.1)',
  color: '#ffffff',
  boxShadow: '0 8px 32px rgba(156, 39, 176, 0.2)',
}));

const StyledFormControl = styled(FormControl)(({ theme }) => ({
  '& .MuiInputLabel-root': {
    color: 'rgba(255, 255, 255, 0.7)',
  },
  '& .MuiOutlinedInput-root': {
    color: '#ffffff',
    '& fieldset': {
      borderColor: 'rgba(255, 255, 255, 0.23)',
    },
    '&:hover fieldset': {
      borderColor: 'rgba(255, 255, 255, 0.5)',
    },
    '&.Mui-focused fieldset': {
      borderColor: '#9c27b0',
    },
  },
  '& .MuiSelect-icon': {
    color: 'rgba(255, 255, 255, 0.7)',
  },
}));

const StyledTextField = styled(TextField)(({ theme }) => ({
  '& .MuiInputLabel-root': {
    color: 'rgba(255, 255, 255, 0.7)',
  },
  '& .MuiOutlinedInput-root': {
    color: '#ffffff',
    '& fieldset': {
      borderColor: 'rgba(255, 255, 255, 0.23)',
    },
    '&:hover fieldset': {
      borderColor: 'rgba(255, 255, 255, 0.5)',
    },
    '&.Mui-focused fieldset': {
      borderColor: '#9c27b0',
    },
  },
}));

const StyledButton = styled(Button)(({ theme }) => ({
  padding: '12px 32px',
  borderRadius: '50px',
  fontSize: '1.1rem',
  background: 'linear-gradient(45deg, #9C27B0 30%, #E040FB 90%)',
  boxShadow: '0 3px 20px rgba(156, 39, 176, 0.3)',
  color: 'white',
  border: 'none',
  transition: 'all 0.3s ease-in-out',
  '&:hover': {
    transform: 'translateY(-2px)',
    boxShadow: '0 5px 25px rgba(156, 39, 176, 0.5)',
  },
}));

const ImageContainer = styled(Box)(({ theme }) => ({
  marginBottom: theme.spacing(3),
  padding: theme.spacing(3),
  backgroundColor: 'rgba(255, 255, 255, 0.05)',
  borderRadius: '16px',
  border: '1px solid rgba(255, 255, 255, 0.1)',
  backdropFilter: 'blur(10px)',
  display: 'flex',
  flexDirection: 'column',
  alignItems: 'center',
  gap: theme.spacing(2),
  transition: 'transform 0.3s ease-in-out',
  '&:hover': {
    transform: 'translateY(-5px)',
  },
}));

const ResultBox = styled(Box)(({ theme }) => ({
  marginTop: theme.spacing(3),
  padding: theme.spacing(3),
  backgroundColor: 'rgba(255, 255, 255, 0.05)',
  borderRadius: '16px',
  border: '1px solid rgba(255, 255, 255, 0.1)',
  backdropFilter: 'blur(10px)',
  textAlign: 'center',
  '& .score': {
    fontSize: '2rem',
    fontWeight: 'bold',
    background: 'linear-gradient(45deg, #9C27B0 30%, #E040FB 90%)',
    WebkitBackgroundClip: 'text',
    WebkitTextFillColor: 'transparent',
    marginBottom: theme.spacing(2),
  },
}));

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
    <div className="relative min-h-screen w-full overflow-hidden bg-[#030303]">
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

      <StyledContainer maxWidth="md">
        <Typography variant="h3" component="h1" sx={{ color: '#fff', mb: 3 }}>
          Spelling Test
        </Typography>

        <StyledPaper elevation={0}>
          <StyledFormControl fullWidth sx={{ mb: 3 }}>
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
          </StyledFormControl>

          {loading ? (
            <Box display="flex" justifyContent="center">
              <CircularProgress sx={{ color: '#9c27b0' }} />
            </Box>
          ) : words.length > 0 && !testStarted ? (
            <Box display="flex" justifyContent="center">
              <StyledButton onClick={startTest}>
                Start Test
              </StyledButton>
            </Box>
          ) : null}

          {testStarted && getCurrentWord() && (
            <Fade in={true}>
              <Box sx={{ textAlign: 'center' }}>
                <ImageContainer>
                  <img 
                    src={getImageUrl(getCurrentWord().image_url)} 
                    alt="Word to spell"
                    style={{ 
                      maxWidth: '200px', 
                      height: 'auto',
                      borderRadius: '12px',
                      boxShadow: '0 8px 32px rgba(156, 39, 176, 0.2)',
                    }}
                  />
                  <Typography variant="h6" sx={{ color: '#fff', mt: 2 }}>
                    Hint: {getCurrentWord().hint}
                  </Typography>
                </ImageContainer>

                <StyledTextField
                  fullWidth
                  label="Type the word"
                  value={userInput}
                  onChange={(e) => setUserInput(e.target.value)}
                  sx={{ mb: 3 }}
                />

                <StyledButton
                  onClick={handleSubmit}
                  disabled={!userInput}
                >
                  Submit
                </StyledButton>
              </Box>
            </Fade>
          )}

          {result && (
            <Fade in={true}>
              <ResultBox>
                <Typography className="score">
                  Score: {Math.round(result.score)}%
                </Typography>
                <Typography variant="h6" sx={{ color: '#fff', mb: 2 }}>
                  Accuracy: {Math.round(result.accuracy * 100)}%
                </Typography>
                {result.dyslexia_indicator > 0.3 && (
                  <Typography 
                    variant="body1" 
                    sx={{ 
                      color: 'rgba(255, 255, 255, 0.7)',
                      backgroundColor: 'rgba(255, 152, 0, 0.1)',
                      p: 2,
                      borderRadius: '8px',
                      border: '1px solid rgba(255, 152, 0, 0.2)',
                    }}
                  >
                    Some spelling patterns suggest potential dyslexia indicators.
                    Consider consulting with an education specialist.
                  </Typography>
                )}
              </ResultBox>
            </Fade>
          )}
        </StyledPaper>
      </StyledContainer>

      <div className="absolute inset-0 bg-gradient-to-t from-[#030303] via-transparent to-[#030303]/80 pointer-events-none" />
    </div>
  );
};

export default SpellingTest; 