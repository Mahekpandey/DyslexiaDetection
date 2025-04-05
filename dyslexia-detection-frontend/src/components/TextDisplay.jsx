import React from 'react';
import { Paper } from '@mui/material';
import { styled } from '@mui/material/styles';

const TextContainer = styled(Paper)(({ theme }) => ({
  padding: theme.spacing(4),
  backgroundColor: '#1a1a1a',
  color: '#ffffff',
  fontFamily: 'OpenDyslexic, Arial, sans-serif',
  fontSize: '1.4rem',
  lineHeight: 1.8,
  letterSpacing: '0.03em',
  wordSpacing: '0.16em',
  borderRadius: '12px',
  boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)',
  maxHeight: '400px',
  overflowY: 'auto',
  '&::-webkit-scrollbar': {
    width: '8px',
  },
  '&::-webkit-scrollbar-track': {
    background: '#2d2d2d',
    borderRadius: '4px',
  },
  '&::-webkit-scrollbar-thumb': {
    background: '#666',
    borderRadius: '4px',
    '&:hover': {
      background: '#888',
    },
  },
  '& .highlighted': {
    backgroundColor: 'rgba(156, 39, 176, 0.3)',
    borderRadius: '4px',
    padding: '0 4px',
    margin: '0 -4px',
    transition: 'background-color 0.2s ease-in-out',
  }
}));

const TextDisplay = ({ text, currentCharIndex, wordBoundaries, isPlaying }) => {
  if (!text) return null;

  const renderText = () => {
    let result = [];
    let lastIndex = 0;

    // Sort boundaries by start position to ensure correct order
    const sortedBoundaries = [...wordBoundaries].sort((a, b) => a.start - b.start);

    sortedBoundaries.forEach((boundary, index) => {
      // Add text before the word
      if (boundary.start > lastIndex) {
        result.push(
          <span key={`text-${index}`}>
            {text.slice(lastIndex, boundary.start)}
          </span>
        );
      }

      // Add the word with highlighting if it contains the current character
      const isHighlighted = 
        isPlaying && 
        currentCharIndex >= boundary.start && 
        currentCharIndex <= boundary.end;

      result.push(
        <span
          key={`word-${index}`}
          className={isHighlighted ? 'highlighted' : ''}
        >
          {text.slice(boundary.start, boundary.end)}
        </span>
      );

      lastIndex = boundary.end;
    });

    // Add any remaining text
    if (lastIndex < text.length) {
      result.push(
        <span key="text-end">
          {text.slice(lastIndex)}
        </span>
      );
    }

    return result;
  };

  return (
    <TextContainer>
      {renderText()}
    </TextContainer>
  );
};

export default TextDisplay; 