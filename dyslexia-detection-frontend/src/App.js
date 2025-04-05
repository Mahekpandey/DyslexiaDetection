import React, { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import {
  Box,
  Container,
  Typography,
  Paper,
  CircularProgress,
  Alert,
  Zoom,
  Fade,
  AppBar,
  Toolbar,
  Button,
} from '@mui/material';
import { styled, keyframes } from '@mui/material/styles';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';
import EmojiPeopleIcon from '@mui/icons-material/EmojiPeople';
import { Routes, Route, Link } from 'react-router-dom';
import HandwritingAnalysis from './components/HandwritingAnalysis';
import OCRPage from './components/OCRPage';
import ReadingAssessment from './pages/ReadingAssessment';
import SpellingTest from './pages/SpellingTest';
import WhackAMole from './pages/WhackAMole/WhackAMole';
import WhackAMoleResults from './pages/WhackAMole/WhackAMoleResults';

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
  '& .MuiTypography-h3': {
    marginBottom: theme.spacing(4),
    textAlign: 'center',
    animation: `${float} 3s ease-in-out infinite`,
  },
}));

const DropzoneArea = styled(Paper)(({ theme }) => ({
  padding: theme.spacing(6),
  textAlign: 'center',
  cursor: 'pointer',
  border: `3px dashed ${theme.palette.primary.main}`,
  borderRadius: theme.shape.borderRadius * 2,
  backgroundColor: 'rgba(156, 39, 176, 0.1)',
  transition: 'all 0.3s ease-in-out',
  '&:hover': {
    borderColor: theme.palette.secondary.main,
    backgroundColor: 'rgba(156, 39, 176, 0.2)',
    transform: 'scale(1.02)',
  },
  '& .MuiSvgIcon-root': {
    fontSize: 64,
    marginBottom: theme.spacing(2),
    color: theme.palette.primary.main,
    animation: `${bounce} 2s infinite`,
  },
}));

const PreviewImage = styled('img')({
  maxWidth: '100%',
  maxHeight: '300px',
  borderRadius: '16px',
  boxShadow: '0 8px 32px rgba(156, 39, 176, 0.4)',
  transition: 'transform 0.3s ease-in-out',
  '&:hover': {
    transform: 'scale(1.05)',
  },
});

const ResultPaper = styled(Paper)(({ theme }) => ({
  padding: theme.spacing(4),
  textAlign: 'center',
  position: 'relative',
  overflow: 'hidden',
  '&::before': {
    content: '""',
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    height: '4px',
    background: 'linear-gradient(45deg, #9C27B0 30%, #E1BEE7 90%)',
  },
}));

function App() {
  const [preview, setPreview] = useState(null);
  const [prediction, setPrediction] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const onDrop = useCallback((acceptedFiles) => {
    const selectedFile = acceptedFiles[0];
    if (selectedFile) {
      setPreview(URL.createObjectURL(selectedFile));
      handlePrediction(selectedFile);
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'image/*': ['.jpeg', '.jpg', '.png']
    },
    multiple: false,
  });

  const handlePrediction = async (file) => {
    setLoading(true);
    setError(null);
    setPrediction(null);

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch('http://localhost:5000/predict', {
        method: 'POST',
        body: formData,
      });

      const data = await response.json();

      if (data.error) {
        throw new Error(data.error);
      }

      setPrediction(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box sx={{ flexGrow: 1 }}>
      <AppBar position="static">
        <Toolbar>
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            Dyslexia Detection
          </Typography>
          <Button color="inherit" component={Link} to="/">
            Handwriting Analysis
          </Button>
          <Button color="inherit" component={Link} to="/ocr">
            OCR Reader
          </Button>
          <Button color="inherit" component={Link} to="/reading">
            Reading Assessment
          </Button>
          <Button color="inherit" component={Link} to="/spelling">
            Spelling Test
          </Button>
          <Button color="inherit" component={Link} to="/whackamole">
            Response Time Test
          </Button>
        </Toolbar>
      </AppBar>

      <Container>
        <Routes>
          <Route path="/" element={<HandwritingAnalysis />} />
          <Route path="/ocr" element={<OCRPage />} />
          <Route path="/reading" element={<ReadingAssessment />} />
          <Route path="/spelling" element={<SpellingTest />} />
          <Route path="/whackamole" element={<WhackAMole />} />
          <Route path="/whackamole-results" element={<WhackAMoleResults />} />
        </Routes>
      </Container>
    </Box>
  );
}

export default App;