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
} from '@mui/material';
import { styled, keyframes } from '@mui/material/styles';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';
import EmojiPeopleIcon from '@mui/icons-material/EmojiPeople';

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

function HandwritingAnalysis() {
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
    <StyledContainer maxWidth="md" sx={{ py: 6 }}>
      <Typography variant="h3" component="h1">
        Let's Check Your Handwriting!
        <EmojiPeopleIcon sx={{ ml: 2, fontSize: 40 }} />
      </Typography>

      <Zoom in={true} timeout={800}>
        <Box sx={{ mb: 4 }}>
          <DropzoneArea {...getRootProps()}>
            <input {...getInputProps()} />
            <CloudUploadIcon />
            <Box sx={{ p: 3 }}>
              {isDragActive ? (
                <Typography variant="h6">Drop your magical handwriting here! ✨</Typography>
              ) : (
                <Typography variant="h6">
                  Drop your handwriting here, or click to choose! 🎨
                </Typography>
              )}
              <Typography variant="body2" sx={{ mt: 2, color: 'text.secondary' }}>
                We can read JPEG, JPG, and PNG - just like magic! 🪄
              </Typography>
            </Box>
          </DropzoneArea>
        </Box>
      </Zoom>

      {preview && (
        <Fade in={true} timeout={1000}>
          <Paper elevation={6} sx={{ p: 3, mb: 4 }}>
            <Typography variant="h6" gutterBottom>Your Magical Writing ✨</Typography>
            <PreviewImage src={preview} alt="Preview" />
          </Paper>
        </Fade>
      )}

      {loading && (
        <Box sx={{ display: 'flex', justifyContent: 'center', my: 4 }}>
          <CircularProgress size={60} thickness={5} color="secondary" />
        </Box>
      )}

      {error && (
        <Fade in={true}>
          <Alert 
            severity="error" 
            sx={{ 
              mb: 4,
              borderRadius: 4,
              animation: `${bounce} 1s ease`
            }}
          >
            Oops! {error} 🎭
          </Alert>
        </Fade>
      )}

      {prediction && (
        <Fade in={true} timeout={1000}>
          <ResultPaper elevation={6}>
            <Typography variant="h6" gutterBottom>The Results Are In! 🎉</Typography>
            <Typography variant="h5" sx={{ my: 2, color: 'primary.light' }}>
              {prediction.prediction}
            </Typography>
            <Typography variant="body1" sx={{ color: 'secondary.main' }}>
              Confidence: <strong>{prediction.confidence}</strong> ⭐
            </Typography>
          </ResultPaper>
        </Fade>
      )}
    </StyledContainer>
  );
}

export default HandwritingAnalysis; 