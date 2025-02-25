# Dyslexia Detection using CNN

This project implements a Convolutional Neural Network (CNN) to detect dyslexia through handwriting analysis.

## Setup

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

2. Ensure your data is organized in the following structure:
```
data/
├── dyslexic/
│   └── *.jpg
└── non_dyslexic/
    └── *.jpg
```

## Training the Model

Run the training script:
```bash
python model.py
```

The script will:
1. Load and preprocess the handwriting images
2. Create and train the CNN model
3. Save the best model to `models/best_model.h5`
4. Generate training history plots
5. Save model summary to `model_summary.txt`

## Model Details

- Input: Grayscale handwriting images (128x128 pixels)
- Architecture: CNN with 3 convolutional blocks
- Output: Binary classification (dyslexic/non-dyslexic)
- Training: Uses data augmentation and early stopping
- Evaluation: Accuracy and AUC metrics

## Files Generated
- `models/best_model.h5`: Best performing model weights
- `models/final_model.h5`: Final model weights
- `training_history.png`: Training and validation metrics plots
- `model_summary.txt`: Model architecture summary 