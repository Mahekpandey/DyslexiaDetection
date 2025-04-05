import React, { useState, useCallback, useEffect, Suspense, lazy, useRef } from 'react';
import { useDropzone } from 'react-dropzone';
import {
  Box,
  Container,
  Typography,
  Paper,
  CircularProgress,
  Alert,
  Button,
  IconButton,
  Tooltip,
  Snackbar,
  LinearProgress,
} from '@mui/material';
import { styled } from '@mui/material/styles';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';
import PlayArrowIcon from '@mui/icons-material/PlayArrow';
import StopIcon from '@mui/icons-material/Stop';
import ImageIcon from '@mui/icons-material/Image';
import CloseIcon from '@mui/icons-material/Close';
import { compressImage } from '../utils/imageCompression';
import config from '../config';

// Lazy load components
const TextDisplay = lazy(() => import('./TextDisplay'));
const AudioControls = lazy(() => import('./AudioControls'));

// Styled components
const StyledContainer = styled(Container)(({ theme }) => ({
  paddingTop: theme.spacing(4),
  paddingBottom: theme.spacing(4),
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
}));

const PreviewImage = styled('img')({
  maxWidth: '100%',
  maxHeight: '300px',
  borderRadius: '8px',
  marginTop: '16px',
});

// Add new validation constants
const MAX_FILE_SIZE = 10 * 1024 * 1024; // 10MB
const SUPPORTED_FORMATS = ['image/jpeg', 'image/jpg', 'image/png'];

// Add new constants
const WORD_DURATION = 300; // Increased for better sync
const AUDIO_CACHE = new Map();
const SPEECH_CACHE = new Map();

const MAX_RETRIES = 3;
const RETRY_DELAY = 1000; // 1 second

function OCRPage() {
  const [preview, setPreview] = useState(null);
  const [extractedText, setExtractedText] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [audioElement, setAudioElement] = useState(null);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'info' });
  const [compressing, setCompressing] = useState(false);
  const [currentWord, setCurrentWord] = useState('');
  const [playbackSpeed, setPlaybackSpeed] = useState(1);
  const [isCached, setIsCached] = useState(false);
  const [isGeneratingAudio, setIsGeneratingAudio] = useState(false);
  const [currentCharIndex, setCurrentCharIndex] = useState(0);
  const [utterance, setUtterance] = useState(null);
  const [wordBoundaries, setWordBoundaries] = useState([]);
  const speechSynthesis = window.speechSynthesis;

  // Clear error when component unmounts
  useEffect(() => {
    return () => {
      if (speechSynthesis) {
        speechSynthesis.cancel();
      }
      if (preview) URL.revokeObjectURL(preview);
      if (audioElement) {
        audioElement.pause();
        URL.revokeObjectURL(audioElement.src);
      }
    };
  }, [preview, audioElement]);

  const showNotification = (message, severity = 'info') => {
    setSnackbar({ open: true, message, severity });
  };

  const handleCloseSnackbar = () => {
    setSnackbar(prev => ({ ...prev, open: false }));
  };

  const validateFile = (file) => {
    if (!file) {
      throw new Error('Please select a file to upload');
    }

    if (!SUPPORTED_FORMATS.includes(file.type)) {
      throw new Error('Unsupported file format. Please upload a JPEG or PNG image');
    }

    if (file.size > MAX_FILE_SIZE) {
      throw new Error('File size too large. Maximum size is 10MB');
    }

    return true;
  };

  const cleanupText = (text) => {
    return text
      // Remove extra whitespace
      .replace(/\s+/g, ' ')
      // Fix common OCR errors
      .replace(/U8/g, 'us')
      .replace(/ell/g, 'all')
      .replace(/Ar}\s*a0\s*!\s*a1/g, 'Ar! ar! ar!')
      .replace(/\|\s*/g, '')
      .replace(/[""]/g, '"')
      .replace(/[-–—]{2,}/g, '...')
      .trim();
  };

  const handleOCR = async (file) => {
    setLoading(true);
    setError(null);
    setExtractedText('');
    setUploadProgress(0);

    try {
      validateFile(file);

      // Compress image before upload
      setCompressing(true);
      showNotification('Compressing image...', 'info');
      const compressedFile = await compressImage(file);
      setCompressing(false);

      // Check server health first
      const healthCheck = await fetch('http://localhost:5001/api/ocr/health')
        .catch(() => {
          throw new Error('OCR server is not responding. Please ensure the backend is running.');
        });

      if (!healthCheck.ok) {
        throw new Error('OCR service is currently unavailable');
      }

      const formData = new FormData();
      formData.append('file', compressedFile);

      const xhr = new XMLHttpRequest();
      const promise = new Promise((resolve, reject) => {
        xhr.upload.addEventListener('progress', (event) => {
          if (event.lengthComputable) {
            const progress = Math.round((event.loaded * 100) / event.total);
            setUploadProgress(progress);
          }
        });

        xhr.onload = () => resolve(xhr.response);
        xhr.onerror = () => reject(new Error('Network error occurred'));
      });

      xhr.open('POST', 'http://localhost:5001/api/ocr/upload');
      xhr.send(formData);

      const response = await promise;
      const data = JSON.parse(response);

      if (!data.success) {
        throw new Error(data.error || 'Failed to process image');
      }

      const easyOCRText = data.easyocr_text || '';
      const tesseractText = data.tesseract_text || '';
      let combinedText = easyOCRText || tesseractText || data.text || '';

      if (!combinedText) {
        throw new Error('No text could be extracted from the image. Please try a clearer image.');
      }

      combinedText = cleanupText(combinedText);
      setExtractedText(combinedText);
      showNotification('Text extracted successfully!', 'success');
      
      if (combinedText) {
        await handleTextTransform(combinedText);
      }
      
    } catch (err) {
      console.error('OCR Error:', err);
      setError(err.message);
      showNotification(err.message, 'error');
    } finally {
      setLoading(false);
      setUploadProgress(0);
      setCompressing(false);
    }
  };

  const handleTextTransform = async (text) => {
    try {
      const response = await fetch('http://localhost:5001/api/ocr/transform', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ text }),
      });

      const data = await response.json();

      if (!data.success) {
        throw new Error(data.error || 'Failed to transform text');
      }

    } catch (err) {
      setError(err.message);
    }
  };

  const calculateWordBoundaries = (text) => {
    const boundaries = [];
    let inWord = false;
    let wordStart = 0;
    
    for (let i = 0; i < text.length; i++) {
      const isWordChar = /\S/.test(text[i]);
      
      if (!inWord && isWordChar) {
        wordStart = i;
        inWord = true;
      } else if (inWord && !isWordChar) {
        boundaries.push({
          start: wordStart,
          end: i,
          word: text.slice(wordStart, i)
        });
        inWord = false;
      }
    }
    
    // Handle last word if text ends with a word
    if (inWord) {
      boundaries.push({
        start: wordStart,
        end: text.length,
        word: text.slice(wordStart)
      });
    }
    
    return boundaries;
  };

  const highlightWords = (text) => {
    const boundaries = calculateWordBoundaries(text);
    setWordBoundaries(boundaries);
    
    const newUtterance = new SpeechSynthesisUtterance(text);
    newUtterance.rate = playbackSpeed;
    
    // Use character position for more accurate highlighting
    newUtterance.onboundary = (event) => {
      if (event.name === 'word') {
        const charIndex = event.charIndex;
        setCurrentCharIndex(charIndex);
        
        // Find the word that contains this character index
        const currentWordBoundary = boundaries.find(
          b => charIndex >= b.start && charIndex <= b.end
        );
        
        if (currentWordBoundary) {
          setCurrentWord(currentWordBoundary.word);
        }
      }
    };

    newUtterance.onend = () => {
      setIsPlaying(false);
      setCurrentWord('');
      setCurrentCharIndex(0);
    };

    newUtterance.onpause = () => {
      setIsPlaying(false);
    };

    newUtterance.onresume = () => {
      setIsPlaying(true);
    };

    newUtterance.onerror = (event) => {
      console.error('Speech synthesis error:', event);
      setError('Error during speech synthesis');
      setIsPlaying(false);
      setCurrentWord('');
      setCurrentCharIndex(0);
    };

    setUtterance(newUtterance);
    return newUtterance;
  };

  const sleep = (ms) => new Promise(resolve => setTimeout(resolve, ms));

  const generateSpeech = async (text, speed, retry = 0) => {
    try {
      const response = await fetch(`${config.API_BASE_URL}${config.endpoints.OCR_SPEECH}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          text,
          engine: 'gtts',
          speed
        }),
      });

      if (!response.ok) {
        const errorData = await response.text();
        throw new Error(`Speech generation failed: ${errorData}`);
      }

      const blob = await response.blob();
      if (blob.size === 0) {
        throw new Error('Received empty audio data');
      }

      return blob;
    } catch (error) {
      if (retry < MAX_RETRIES) {
        console.log(`Retrying speech generation (${retry + 1}/${MAX_RETRIES})...`);
        await sleep(RETRY_DELAY);
        return generateSpeech(text, speed, retry + 1);
      }
      throw error;
    }
  };

  const handleTextToSpeech = () => {
    if (!extractedText) {
      showNotification('No text available for speech', 'error');
      return;
    }

    try {
      setIsGeneratingAudio(true);
      
      // Cancel any ongoing speech
      speechSynthesis.cancel();
      
      // Reset state
      setCurrentWord('');
      setCurrentCharIndex(0);
      
      const newUtterance = highlightWords(extractedText);
      setIsPlaying(true);
      speechSynthesis.speak(newUtterance);
      
    } catch (err) {
      console.error('TTS Error:', err);
      setError(err.message);
      showNotification(err.message, 'error');
    } finally {
      setIsGeneratingAudio(false);
    }
  };

  const handleSpeedChange = (newSpeed) => {
    setPlaybackSpeed(newSpeed);
    if (utterance) {
      const currentlyPlaying = isPlaying;
      speechSynthesis.cancel();
      utterance.rate = newSpeed;
      if (currentlyPlaying) {
        speechSynthesis.speak(utterance);
      }
    }
  };

  const toggleAudio = () => {
    if (isPlaying) {
      speechSynthesis.cancel();
      setIsPlaying(false);
      setCurrentWord('');
      setCurrentCharIndex(0);
    } else {
      handleTextToSpeech();
    }
  };

  const onDrop = useCallback((acceptedFiles) => {
    const selectedFile = acceptedFiles[0];
    if (selectedFile) {
      setPreview(URL.createObjectURL(selectedFile));
      handleOCR(selectedFile);
    }
  }, [handleOCR]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'image/*': ['.jpeg', '.jpg', '.png']
    },
    multiple: false,
  });

  return (
    <StyledContainer maxWidth="md">
      <Typography variant="h4" gutterBottom align="center" sx={{ color: '#fff' }}>
        OCR Text Reader
      </Typography>

      <DropzoneArea {...getRootProps()}>
        <input {...getInputProps()} />
        <CloudUploadIcon sx={{ fontSize: 48, color: 'primary.main', mb: 2 }} />
        <Typography variant="h6" sx={{ color: '#fff' }}>
          {isDragActive
            ? "Drop the image here!"
            : "Drag & drop an image, or click to select"}
        </Typography>
        <Typography variant="body2" sx={{ color: 'rgba(255, 255, 255, 0.7)', mt: 1 }}>
          Supports JPG, JPEG, PNG
        </Typography>
      </DropzoneArea>

      {(loading || compressing) && (
        <Box sx={{ width: '100%', mt: 2 }}>
          <LinearProgress 
            variant={compressing ? "indeterminate" : "determinate"} 
            value={uploadProgress} 
          />
          <Typography variant="body2" sx={{ color: '#fff', mt: 1, textAlign: 'center' }}>
            {compressing 
              ? 'Compressing image...' 
              : uploadProgress < 100 
                ? `Uploading: ${uploadProgress}%` 
                : 'Processing image...'}
          </Typography>
        </Box>
      )}

      {error && (
        <Alert 
          severity="error" 
          sx={{ mt: 2 }}
          action={
            <IconButton
              aria-label="close"
              color="inherit"
              size="small"
              onClick={() => setError(null)}
            >
              <CloseIcon fontSize="inherit" />
            </IconButton>
          }
        >
          {error}
        </Alert>
      )}

      {preview && (
        <Box sx={{ mt: 3, textAlign: 'center' }}>
          <Typography variant="h6" gutterBottom sx={{ color: '#fff' }}>
            Uploaded Image
          </Typography>
          <PreviewImage src={preview} alt="Preview" />
        </Box>
      )}

      {extractedText && (
        <Suspense fallback={<CircularProgress />}>
          <Box sx={{ mt: 3 }}>
            <Typography variant="h6" gutterBottom sx={{ color: '#fff', fontFamily: 'OpenDyslexic, Arial, sans-serif' }}>
              Extracted Text
            </Typography>
            <TextDisplay 
              text={extractedText} 
              currentWord={currentWord}
              currentCharIndex={currentCharIndex}
              wordBoundaries={wordBoundaries}
              isPlaying={isPlaying}
            />
            <AudioControls 
              text={extractedText} 
              isPlaying={isPlaying} 
              onToggle={toggleAudio}
              playbackSpeed={playbackSpeed}
              onSpeedChange={handleSpeedChange}
              isCached={isCached}
              isLoading={isGeneratingAudio}
            />
          </Box>
        </Suspense>
      )}

      <Snackbar
        open={snackbar.open}
        autoHideDuration={6000}
        onClose={handleCloseSnackbar}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
      >
        <Alert 
          onClose={handleCloseSnackbar} 
          severity={snackbar.severity}
          sx={{ width: '100%' }}
        >
          {snackbar.message}
        </Alert>
      </Snackbar>
    </StyledContainer>
  );
}

export default OCRPage; 