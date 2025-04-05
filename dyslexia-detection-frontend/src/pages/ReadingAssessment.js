import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Button,
  Paper,
  CircularProgress,
  Alert,
  Fade,
  Slider,
  Container,
} from '@mui/material';
import { styled, keyframes } from '@mui/material/styles';
import MicIcon from '@mui/icons-material/Mic';
import VolumeUpIcon from '@mui/icons-material/VolumeUp';
import SpeedIcon from '@mui/icons-material/Speed';
import { motion } from 'framer-motion';

const float = keyframes`
  0% { transform: translateY(0px); }
  50% { transform: translateY(-10px); }
  100% { transform: translateY(0px); }
`;

const bounce = keyframes`
  0%, 20%, 50%, 80%, 100% { transform: translateY(0); }
  40% { transform: translateY(-20px); }
  60% { transform: translateY(-10px); }
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

const RecordingIndicator = styled(Box)(({ theme }) => ({
  display: 'flex',
  flexDirection: 'column',
  alignItems: 'center',
  padding: theme.spacing(4),
  backgroundColor: 'rgba(103, 58, 183, 0.15)',
  backdropFilter: 'blur(10px)',
  borderRadius: '20px',
  marginTop: theme.spacing(3),
  color: '#fff',
  border: '1px solid rgba(255, 255, 255, 0.1)',
  boxShadow: '0 8px 32px rgba(156, 39, 176, 0.2)',
  '& .MicIcon': {
    fontSize: 56,
    color: '#fff',
    animation: `${bounce} 1.5s infinite`,
  },
}));

const PassagePaper = styled(Paper)(({ theme }) => ({
  padding: theme.spacing(4),
  marginBottom: theme.spacing(4),
  backgroundColor: 'rgba(42, 42, 42, 0.8)',
  backdropFilter: 'blur(10px)',
  borderRadius: '20px',
  border: '1px solid rgba(255, 255, 255, 0.1)',
  boxShadow: '0 8px 32px rgba(156, 39, 176, 0.2)',
  '& .MuiTypography-body1': {
    fontSize: '1.1rem',
    lineHeight: 1.8,
    color: '#ffffff',
    letterSpacing: '0.02em',
  },
}));

const ResultsPaper = styled(Paper)(({ theme }) => ({
  padding: theme.spacing(4),
  backgroundColor: '#2a2a2a',
  borderRadius: '16px',
  border: '2px solid #673ab7',
  '& .result-item': {
    display: 'flex',
    alignItems: 'center',
    marginBottom: theme.spacing(3),
    padding: theme.spacing(2),
    borderRadius: '12px',
    backgroundColor: '#1a1a1a',
    transition: 'transform 0.2s',
    '&:hover': {
      transform: 'translateX(8px)'
    }
  },
  '& .result-label': {
    color: '#b39ddb',
    fontWeight: 500,
    marginRight: theme.spacing(2),
    minWidth: '160px'
  },
  '& .result-value': {
    fontWeight: 600,
    fontSize: '1.2rem',
    color: '#ffffff'
  },
  '& .result-value-good': {
    color: '#81c784'
  },
  '& .result-value-warning': {
    color: '#ffb74d'
  },
  '& .result-value-poor': {
    color: '#e57373'
  }
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

const PlayButton = styled(Button)(({ theme }) => ({
  minWidth: '40px',
  width: '40px',
  height: '40px',
  borderRadius: '50%',
  padding: 0,
  backgroundColor: '#673ab7',
  color: 'white',
  '&:hover': {
    backgroundColor: '#5e35b1',
  },
}));

const SpeedControl = styled(Box)(({ theme }) => ({
  display: 'flex',
  alignItems: 'center',
  gap: theme.spacing(2),
  padding: theme.spacing(1),
  backgroundColor: '#2a2a2a',
  borderRadius: '8px',
  width: '200px',
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

const ReadingAssessment = () => {
  const [passage, setPassage] = useState('');
  const [recognizedText, setRecognizedText] = useState('');
  const [isRecording, setIsRecording] = useState(false);
  const [analysis, setAnalysis] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);
  const [recordingState, setRecordingState] = useState('idle');
  const [recordingMessage, setRecordingMessage] = useState('');
  const [speechRate, setSpeechRate] = useState(1);
  const [speaking, setSpeaking] = useState(false);

  const startAssessment = async () => {
    try {
      setLoading(true);
      const response = await fetch('http://localhost:5001/api/reading/start', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });
      const data = await response.json();
      if (data.success) {
        setPassage(data.passage);
        setRecognizedText('');
        setAnalysis(null);
        setRecordingState('idle');
        setRecordingMessage('');
      } else {
        setError('Failed to get reading passage');
      }
    } catch (err) {
      setError('Error starting assessment: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  const pollBackendStatus = async () => {
    try {
      const response = await fetch('http://localhost:5001/api/speech/status', {
        method: 'GET',
      });
      const data = await response.json();
      if (data.success) {
        setRecordingState(data.status);
        
        switch (data.status) {
          case 'ADJUSTING':
            setRecordingMessage('Adjusting for ambient noise...');
            break;
          case 'LISTENING':
            setRecordingMessage('Listening...');
            break;
          case 'PROCESSING':
            setRecordingMessage('Recognition in progress...');
            break;
          case 'idle':
            if (data.recognized_text) {
              setRecognizedText(data.recognized_text);
              analyzeReading(data.recognized_text);
            }
            setIsRecording(false);
            break;
          default:
            break;
        }
      }
      return data.status;
    } catch (err) {
      console.error('Error polling status:', err);
      return null;
    }
  };

  useEffect(() => {
    let pollInterval;
    if (isRecording) {
      // Initial poll immediately
      pollBackendStatus();
      // Then poll every 500ms
      pollInterval = setInterval(pollBackendStatus, 500);
    }
    return () => {
      if (pollInterval) clearInterval(pollInterval);
    };
  }, [isRecording]);

  const startRecording = async () => {
    try {
      setIsRecording(true);
      setError(null);
      
      // Initialize recording session
      const initResponse = await fetch('http://localhost:5001/api/speech/init', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ attempt: 1 }),
      });
      
      if (!initResponse.ok) throw new Error('Failed to initialize recording');

      // Start recording
      const recordResponse = await fetch('http://localhost:5001/api/speech/record', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ duration: 30 }),
      });
      
      if (!recordResponse.ok) throw new Error('Recording failed');
      
      const data = await recordResponse.json();
      if (!data.success) {
        throw new Error(data.error || 'Failed to record speech');
      }
    } catch (err) {
      setError('Error recording speech: ' + err.message);
      setIsRecording(false);
    }
  };

  const analyzeReading = async (recognizedText) => {
    try {
      setLoading(true);
      console.log('Backend recognized text:', recognizedText); // Debug log
      
      // Clean up the recognized text
      const cleanedText = recognizedText.trim().toLowerCase();
      console.log('Cleaned recognized text:', cleanedText); // Debug log
      
      const response = await fetch('http://localhost:5001/api/reading/analyze', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          original_text: passage.trim().toLowerCase(),
          recognized_text: cleanedText
        }),
      });
      
      const data = await response.json();
      console.log('Analysis response:', data); // Debug log
      
      if (data.success && data.analysis) {
        // Format the analysis results
        const result = {
          ...data.analysis,
          errors: data.analysis.errors.map(error => ({
            ...error,
            spoken: error.spoken === '(missing)' ? '(missing word)' : error.spoken,
            expected: error.expected || 'unknown'
          }))
        };
        
        setAnalysis(result);
        setRecognizedText(cleanedText);
        
        // Save the result
        await fetch('http://localhost:5001/api/reading/save-result', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(result),
        });
      } else {
        throw new Error(data.error || 'Analysis failed - No results returned');
      }
    } catch (err) {
      console.error('Analysis error:', err); // Debug log
      setError('Error analyzing reading: ' + err.message);
      setAnalysis({
        accuracy: 0,
        words_per_minute: 0,
        dyslexia_prediction: true,
        errors: [],
        recognized_text: recognizedText || '',
        original_text: passage
      });
    } finally {
      setLoading(false);
    }
  };

  // Add speech synthesis function
  const speakWord = (word) => {
    // Cancel any ongoing speech
    window.speechSynthesis.cancel();

    const utterance = new SpeechSynthesisUtterance(word);
    utterance.rate = speechRate;
    utterance.onstart = () => setSpeaking(true);
    utterance.onend = () => setSpeaking(false);
    window.speechSynthesis.speak(utterance);
  };

  // Handle speed change
  const handleSpeedChange = (event, newValue) => {
    setSpeechRate(newValue);
  };

  const renderRecordingState = () => {
    if (recordingState === 'idle') return null;

    return (
      <Fade in={true}>
        <RecordingIndicator>
          <MicIcon className="MicIcon" />
          <Typography variant="h5" sx={{ mt: 2, mb: 1, fontWeight: 'bold' }}>
            {recordingMessage}
          </Typography>
          {recordingState === 'listening' && (
            <Typography variant="body1" sx={{ opacity: 0.8 }}>
              Please read the passage clearly...
            </Typography>
          )}
          {recordingState === 'processing' && (
            <Box sx={{ mt: 2, p: 2, bgcolor: 'rgba(255,255,255,0.1)', borderRadius: 1 }}>
              <Typography variant="body2" sx={{ opacity: 0.9 }}>
                Recognized so far: {recognizedText || 'Listening...'}
              </Typography>
            </Box>
          )}
        </RecordingIndicator>
      </Fade>
    );
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
          Reading Assessment
        </Typography>

        {error && (
          <Alert 
            severity="error" 
            sx={{ 
              mb: 3,
              borderRadius: '12px',
              backgroundColor: 'rgba(211, 47, 47, 0.1)',
              color: '#fff',
              backdropFilter: 'blur(10px)',
              border: '1px solid rgba(255, 255, 255, 0.1)',
              '& .MuiAlert-icon': {
                color: '#ff5252',
              },
            }}
          >
            {error}
          </Alert>
        )}

        <StyledPaper elevation={0}>
          {!passage ? (
            <Box sx={{ textAlign: 'center' }}>
              <StyledButton
                variant="contained"
                onClick={startAssessment}
                disabled={loading}
              >
                {loading ? (
                  <CircularProgress size={24} color="inherit" sx={{ mr: 1 }} />
                ) : 'Start Assessment'}
              </StyledButton>
            </Box>
          ) : (
            <>
              <Typography 
                variant="h6" 
                gutterBottom 
                sx={{ 
                  mb: 3,
                  color: '#ffffff',
                  fontWeight: 500,
                  textAlign: 'center',
                }}
              >
                Read the following passage:
              </Typography>

              <PassagePaper elevation={0}>
                <Typography variant="body1">{passage}</Typography>
              </PassagePaper>

              {!isRecording && !analysis && (
                <Box sx={{ textAlign: 'center' }}>
                  <StyledButton
                    variant="contained"
                    onClick={startRecording}
                    disabled={loading}
                    startIcon={<MicIcon />}
                  >
                    Start Reading
                  </StyledButton>
                </Box>
              )}

              {renderRecordingState()}

              {analysis && (
                <Fade in={true} timeout={1000}>
                  <Box sx={{ mt: 4 }}>
                    <Typography 
                      variant="h6" 
                      gutterBottom 
                      sx={{ 
                        mb: 3,
                        color: '#ffffff',
                        fontWeight: 600,
                        textAlign: 'center'
                      }}
                    >
                      Your Reading Results
                    </Typography>
                    <ResultsPaper elevation={0}>
                      <Box className="result-item">
                        <Typography className="result-label">Accuracy</Typography>
                        <Typography 
                          className={`result-value ${
                            analysis.accuracy >= 90 ? 'result-value-good' :
                            analysis.accuracy >= 70 ? 'result-value-warning' :
                            'result-value-poor'
                          }`}
                        >
                          {analysis.accuracy}%
                        </Typography>
                      </Box>
                      
                      <Box className="result-item">
                        <Typography className="result-label">Reading Speed</Typography>
                        <Typography 
                          className={`result-value ${
                            analysis.words_per_minute >= 100 ? 'result-value-good' :
                            analysis.words_per_minute >= 60 ? 'result-value-warning' :
                            'result-value-poor'
                          }`}
                        >
                          {analysis.words_per_minute} words per minute
                        </Typography>
                      </Box>
                      
                      <Box className="result-item">
                        <Typography className="result-label">Assessment</Typography>
                        <Typography 
                          className={`result-value ${
                            !analysis.dyslexia_prediction ? 'result-value-good' : 'result-value-warning'
                          }`}
                        >
                          {analysis.dyslexia_prediction ? 'May need support' : 'Reading well'}
                        </Typography>
                      </Box>
                      
                      {analysis.errors && analysis.errors.length > 0 && (
                        <Box sx={{ mt: 4 }}>
                          <Typography 
                            variant="h6" 
                            gutterBottom
                            sx={{ 
                              color: '#ffffff',
                              fontWeight: 500,
                              mb: 3,
                              textAlign: 'center'
                            }}
                          >
                            Words to Practice
                          </Typography>
                          
                          <Box sx={{ mb: 3, p: 2, backgroundColor: '#2a2a2a', borderRadius: '12px' }}>
                            <Typography 
                              variant="subtitle1" 
                              sx={{ 
                                color: '#ffffff',
                                fontWeight: 500,
                                mb: 1
                              }}
                            >
                              Original Text:
                            </Typography>
                            <Typography variant="body1" sx={{ color: '#ffffff' }}>
                              {analysis.original_text}
                            </Typography>
                            
                            <Typography 
                              variant="subtitle1" 
                              sx={{ 
                                color: '#ffffff',
                                fontWeight: 500,
                                mt: 2,
                                mb: 1
                              }}
                            >
                              Your Reading:
                            </Typography>
                            <Typography variant="body1" sx={{ color: '#ffffff' }}>
                              {analysis.recognized_text || 'No text recognized'}
                            </Typography>
                          </Box>

                          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                            {analysis.errors.map((error, index) => (
                              <Box 
                                key={index}
                                sx={{
                                  display: 'flex',
                                  alignItems: 'center',
                                  p: 2,
                                  borderRadius: '12px',
                                  backgroundColor: 'rgba(231, 76, 60, 0.05)',
                                  border: '1px solid rgba(231, 76, 60, 0.1)',
                                  transition: 'transform 0.2s',
                                  '&:hover': {
                                    transform: 'translateX(8px)'
                                  }
                                }}
                              >
                                <Box sx={{ 
                                  flex: 1, 
                                  display: 'flex', 
                                  alignItems: 'center', 
                                  justifyContent: 'center',
                                  flexWrap: 'wrap',
                                  gap: 1
                                }}>
                                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                                    <Typography
                                      sx={{
                                        px: 2,
                                        py: 1,
                                        borderRadius: '8px',
                                        backgroundColor: 'rgba(46, 204, 113, 0.1)',
                                        color: '#27ae60',
                                        border: '1px solid rgba(46, 204, 113, 0.2)',
                                        fontWeight: 500,
                                        minWidth: '80px',
                                        textAlign: 'center'
                                      }}
                                    >
                                      {error.expected}
                                    </Typography>
                                    <PlayButton
                                      onClick={() => speakWord(error.expected)}
                                      disabled={speaking}
                                    >
                                      <VolumeUpIcon />
                                    </PlayButton>
                                  </Box>
                                  
                                  <Typography sx={{ 
                                    color: '#e74c3c', 
                                    mx: 2, 
                                    fontSize: '1.2rem',
                                    display: 'flex',
                                    alignItems: 'center'
                                  }}>
                                    →
                                  </Typography>
                                  
                                  <Typography
                                    sx={{
                                      px: 2,
                                      py: 1,
                                      borderRadius: '8px',
                                      backgroundColor: error.spoken === '(missing)' ? 'rgba(231, 76, 60, 0.05)' : 'rgba(231, 76, 60, 0.1)',
                                      color: '#e74c3c',
                                      border: '1px solid rgba(231, 76, 60, 0.2)',
                                      fontWeight: 500,
                                      minWidth: '80px',
                                      textAlign: 'center',
                                      fontStyle: error.spoken === '(missing)' ? 'italic' : 'normal'
                                    }}
                                  >
                                    {error.spoken === '(missing)' ? 'missed' : error.spoken}
                                  </Typography>
                                </Box>
                              </Box>
                            ))}
                          </Box>
                        </Box>
                      )}
                    </ResultsPaper>
                    
                    <Box sx={{ textAlign: 'center', mt: 4 }}>
                      <StyledButton
                        variant="contained"
                        color="primary"
                        onClick={startAssessment}
                        sx={{
                          backgroundColor: '#4CAF50',
                          '&:hover': {
                            backgroundColor: '#388E3C',
                            boxShadow: '0 4px 12px rgba(76, 175, 80, 0.2)',
                          }
                        }}
                      >
                        Try Another Passage
                      </StyledButton>
                    </Box>
                  </Box>
                </Fade>
              )}
            </>
          )}
        </StyledPaper>
      </StyledContainer>

      <div className="absolute inset-0 bg-gradient-to-t from-[#030303] via-transparent to-[#030303]/80 pointer-events-none" />
    </div>
  );
};

export default ReadingAssessment; 