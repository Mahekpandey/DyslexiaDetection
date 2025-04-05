import React from 'react';
import { Box, IconButton, Tooltip, Slider, Typography } from '@mui/material';
import { styled } from '@mui/material/styles';
import PlayArrowIcon from '@mui/icons-material/PlayArrow';
import StopIcon from '@mui/icons-material/Stop';
import FastForwardIcon from '@mui/icons-material/FastForward';
import FastRewindIcon from '@mui/icons-material/FastRewind';

const StyledBox = styled(Box)(({ theme }) => ({
  display: 'flex',
  flexDirection: 'column',
  alignItems: 'center',
  gap: theme.spacing(2),
  marginTop: theme.spacing(2),
}));

const ControlsBox = styled(Box)(({ theme }) => ({
  display: 'flex',
  alignItems: 'center',
  gap: theme.spacing(2),
}));

const SpeedControl = styled(Box)(({ theme }) => ({
  display: 'flex',
  alignItems: 'center',
  gap: theme.spacing(2),
  width: '300px',
  backgroundColor: 'rgba(255, 255, 255, 0.1)',
  padding: theme.spacing(2),
  borderRadius: theme.shape.borderRadius,
}));

const AudioControls = ({ 
  isPlaying, 
  onToggle, 
  playbackSpeed, 
  onSpeedChange,
  isCached,
  isLoading 
}) => {
  const handleSpeedChange = (_, newValue) => {
    onSpeedChange(newValue);
  };

  const speedMarks = [
    { value: 0.5, label: '0.5x' },
    { value: 1, label: '1x' },
    { value: 1.5, label: '1.5x' },
    { value: 2, label: '2x' },
  ];

  return (
    <StyledBox>
      <ControlsBox>
        <Tooltip title={isPlaying ? "Stop" : "Play"}>
          <IconButton
            onClick={onToggle}
            color="primary"
            size="large"
            disabled={isLoading}
            sx={{
              backgroundColor: 'rgba(156, 39, 176, 0.1)',
              '&:hover': {
                backgroundColor: 'rgba(156, 39, 176, 0.2)'
              },
              width: '60px',
              height: '60px'
            }}
          >
            {isPlaying ? <StopIcon /> : <PlayArrowIcon />}
          </IconButton>
        </Tooltip>
      </ControlsBox>

      <SpeedControl>
        <FastRewindIcon />
        <Box sx={{ flex: 1 }}>
          <Slider
            value={playbackSpeed}
            onChange={handleSpeedChange}
            min={0.5}
            max={2}
            step={0.1}
            marks={speedMarks}
            valueLabelDisplay="auto"
            valueLabelFormat={x => `${x}x`}
          />
        </Box>
        <FastForwardIcon />
      </SpeedControl>

      {isCached && (
        <Typography variant="caption" sx={{ color: 'success.main' }}>
          ✓ Audio cached for faster playback
        </Typography>
      )}
      
      {isLoading && (
        <Typography variant="caption" sx={{ color: 'info.main' }}>
          Generating audio...
        </Typography>
      )}
    </StyledBox>
  );
};

export default AudioControls; 