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

const DropzoneArea = styled(Paper)(({ theme }) => ({
  padding: theme.spacing(4),
  maxWidth: '600px',
  margin: '0 auto',
  textAlign: 'center',
  cursor: 'pointer',
  border: `2px dashed ${theme.palette.primary.main}`,
  borderRadius: '20px',
  backgroundColor: 'rgba(156, 39, 176, 0.1)',
  transition: 'all 0.3s ease-in-out',
  '&:hover': {
    borderColor: theme.palette.secondary.main,
    backgroundColor: 'rgba(156, 39, 176, 0.2)',
    transform: 'scale(1.02)',
  },
  '& .MuiSvgIcon-root': {
    fontSize: 48,
    marginBottom: theme.spacing(1),
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

        <ElegantShape
          delay={0.7}
          width={150}
          height={40}
          rotate={-25}
          gradient="from-cyan-500/[0.15]"
          className="left-[20%] md:left-[25%] top-[5%] md:top-[10%]"
        />
      </div>

      <StyledContainer maxWidth="md">
        <Typography variant="h3" component="h1" sx={{ color: '#fff', mb: 3 }}>
          Let's Check Your Handwriting!
          <EmojiPeopleIcon sx={{ ml: 2, fontSize: 40 }} />
        </Typography>

        <Zoom in={true} timeout={800}>
          <Box sx={{ mb: 3 }}>
            <DropzoneArea {...getRootProps()}>
              <input {...getInputProps()} />
              <CloudUploadIcon />
              <Box sx={{ p: 2 }}>
                {isDragActive ? (
                  <Typography variant="h6" sx={{ fontSize: '1.1rem', color: '#fff' }}>
                    Drop your magical handwriting here! ✨
                  </Typography>
                ) : (
                  <Typography variant="h6" sx={{ fontSize: '1.1rem', color: '#fff' }}>
                    Drop your handwriting here, or click to choose! 🎨
                  </Typography>
                )}
                <Typography variant="body2" sx={{ mt: 1, color: 'rgba(255, 255, 255, 0.7)', fontSize: '0.9rem' }}>
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

      <div className="absolute inset-0 bg-gradient-to-t from-[#030303] via-transparent to-[#030303]/80 pointer-events-none" />
    </div>
  );
}

export default HandwritingAnalysis; 