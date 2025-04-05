const fs = require('fs');
const https = require('https');
const path = require('path');

const fonts = [
  {
    name: 'OpenDyslexic-Regular.otf',
    url: 'https://github.com/antijingoist/opendyslexic/raw/master/compiled/OpenDyslexic-Regular.otf'
  },
  {
    name: 'OpenDyslexic-Bold.otf',
    url: 'https://github.com/antijingoist/opendyslexic/raw/master/compiled/OpenDyslexic-Bold.otf'
  }
];

// Create fonts directory if it doesn't exist
const fontsDir = path.join(__dirname, 'fonts');
if (!fs.existsSync(fontsDir)) {
  fs.mkdirSync(fontsDir, { recursive: true });
}

// Download each font
fonts.forEach(font => {
  const filePath = path.join(fontsDir, font.name);
  
  if (!fs.existsSync(filePath)) {
    console.log(`Downloading ${font.name}...`);
    
    https.get(font.url, (response) => {
      const fileStream = fs.createWriteStream(filePath);
      response.pipe(fileStream);
      
      fileStream.on('finish', () => {
        console.log(`Downloaded ${font.name}`);
      });
    }).on('error', (err) => {
      console.error(`Error downloading ${font.name}:`, err.message);
    });
  } else {
    console.log(`${font.name} already exists`);
  }
}); 