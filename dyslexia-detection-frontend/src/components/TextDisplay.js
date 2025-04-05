import React, { useEffect, useRef } from 'react';
import { Paper } from '@mui/material';
import { styled } from '@mui/material/styles';

const StyledPaper = styled(Paper)(({ theme }) => ({
  padding: theme.spacing(4),
  marginTop: theme.spacing(3),
  marginBottom: theme.spacing(3),
  backgroundColor: '#ffffff',
  color: '#000000',
  fontFamily: 'OpenDyslexic, Arial, sans-serif',
  fontSize: '1.4rem',
  lineHeight: '1.8',
  letterSpacing: '0.5px',
  wordSpacing: '3px',
  borderRadius: '12px',
  boxShadow: '0 4px 20px rgba(0, 0, 0, 0.1)',
  '& p': {
    margin: '1em 0',
  },
  '& .word': {
    display: 'inline-block',
    padding: '0 2px',
    margin: '0 1px',
    borderRadius: '4px',
    transition: 'background-color 0.2s ease',
  },
  '& .highlighted': {
    backgroundColor: 'rgba(156, 39, 176, 0.2)',
  }
}));

const TextDisplay = ({ text, currentWord, isPlaying }) => {
  const containerRef = useRef(null);

  useEffect(() => {
    if (isPlaying && currentWord && containerRef.current) {
      const highlightedElement = containerRef.current.querySelector('.highlighted');
      if (highlightedElement) {
        highlightedElement.scrollIntoView({
          behavior: 'smooth',
          block: 'center',
        });
      }
    }
  }, [currentWord, isPlaying]);

  const renderWords = (paragraph) => {
    return paragraph.split(' ').map((word, index) => (
      <span
        key={index}
        className={`word ${word === currentWord ? 'highlighted' : ''}`}
      >
        {word}{' '}
      </span>
    ));
  };

  return (
    <StyledPaper elevation={3} ref={containerRef}>
      {text.split('\n').map((paragraph, index) => (
        <p key={index}>{renderWords(paragraph)}</p>
      ))}
    </StyledPaper>
  );
};

export default TextDisplay; 