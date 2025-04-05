import React from 'react';
import { Box } from '@mui/material';
import { Routes, Route } from 'react-router-dom';
import HandwritingAnalysis from './components/HandwritingAnalysis';
import OCRPage from './components/OCRPage';
import ReadingAssessment from './pages/ReadingAssessment';
import SpellingTest from './pages/SpellingTest';
import WhackAMole from './pages/WhackAMole/WhackAMole';
import WhackAMoleResults from './pages/WhackAMole/WhackAMoleResults';
import { HeroGeometric } from './components/ui/shape-landing-hero.tsx';
import { NavBar } from './components/ui/tubelight-navbar.tsx';
import { 
  Home,
  Edit,
  FileText,
  BookOpen,
  SpellCheck,
  Timer
} from 'lucide-react';

function App() {
  const navItems = [
    { name: 'Home', url: '/', icon: Home },
    { name: 'Handwriting', url: '/handwriting-analysis', icon: Edit },
    { name: 'OCR Reader', url: '/ocr', icon: FileText },
    { name: 'Reading', url: '/reading', icon: BookOpen },
    { name: 'Spelling', url: '/spelling', icon: SpellCheck },
    { name: 'Response Time', url: '/whackamole', icon: Timer }
  ];

  return (
    <Box sx={{ flexGrow: 1 }}>
      <NavBar items={navItems} />

      <Routes>
        <Route path="/" element={<HeroGeometric />} />
        <Route path="/handwriting-analysis" element={<HandwritingAnalysis />} />
        <Route path="/ocr" element={<OCRPage />} />
        <Route path="/reading" element={<ReadingAssessment />} />
        <Route path="/spelling" element={<SpellingTest />} />
        <Route path="/whackamole" element={<WhackAMole />} />
        <Route path="/whackamole-results" element={<WhackAMoleResults />} />
      </Routes>
    </Box>
  );
}

export default App;