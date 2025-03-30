import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms
import numpy as np
from pathlib import Path
import cv2
from sklearn.model_selection import train_test_split
import matplotlib
matplotlib.use('Agg')  # Use Agg backend instead of Tkinter
import matplotlib.pyplot as plt
import os

class HandwritingDataset(Dataset):
    """Custom Dataset for handwriting images"""
    def __init__(self, images, labels, transform=None, is_training=False):
        self.images = torch.FloatTensor(images)  # Shape: (N, 1, H, W)
        self.labels = torch.FloatTensor(labels).reshape(-1, 1)
        self.transform = transform
        self.is_training = is_training
        
        # Data augmentation for training
        if is_training:
            self.train_transforms = transforms.Compose([
                transforms.ToPILImage(),
                transforms.RandomRotation(10),
                transforms.RandomAffine(degrees=0, translate=(0.1, 0.1)),
                transforms.RandomPerspective(distortion_scale=0.2, p=0.5),
                transforms.ToTensor(),
            ])

    def __len__(self):
        return len(self.images)

    def __getitem__(self, idx):
        image = self.images[idx]  # Shape: (1, H, W)
        label = self.labels[idx]
        
        if self.is_training:
            image = self.train_transforms(image)
        
        if self.transform:
            image = self.transform(image.numpy())
        
        return image, label

def load_and_preprocess_data(data_dir='DyslexiaDetection/data', img_size=(128, 128)):
    """
    Load and preprocess images from the data directory.
    Using smaller image size (128x128) for faster training.
    """
    X = []
    y = []
    
    for class_dir, label in [('dyslexic', 1), ('non_dyslexic', 0)]:
        path = Path(data_dir) / class_dir
        for img_path in path.glob('*.jpg'):
            try:
                # Read image in grayscale
                img = cv2.imread(str(img_path), cv2.IMREAD_GRAYSCALE)
                if img is None:
                    continue
                
                # Resize
                img = cv2.resize(img, img_size)
                
                # Convert to float32 and normalize to [0, 1]
                img = img.astype(np.float32) / 255.0
                
                # Apply CLAHE for contrast enhancement
                clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
                img = clahe.apply(np.uint8(img * 255)).astype(np.float32) / 255.0
                
                # Apply Gaussian blur to reduce noise
                img = cv2.GaussianBlur(img, (3,3), 0)
                
                # Add channel dimension
                img = np.expand_dims(img, axis=0)  # Shape: (1, H, W)
                
                X.append(img)
                y.append(label)
                
            except Exception as e:
                print(f"Error processing {img_path}: {e}")
    
    if not X:
        raise ValueError("No images were successfully loaded!")
    
    X = np.array(X, dtype=np.float32)  # Shape: (N, 1, H, W)
    y = np.array(y, dtype=np.float32)
    
    print(f"Successfully loaded {len(X)} images")
    print(f"Image shape: {X.shape}")
    
    return X, y

class DyslexiaCNN(nn.Module):
    """CNN model for dyslexia detection"""
    def __init__(self, dropout_rate=0.2):
        super(DyslexiaCNN, self).__init__()
        
        # Simpler architecture with fewer parameters
        self.features = nn.Sequential(
            # First block
            nn.Conv2d(1, 16, kernel_size=3, padding=1),
            nn.BatchNorm2d(16),
            nn.ReLU(),
            nn.MaxPool2d(2),
            
            # Second block
            nn.Conv2d(16, 32, kernel_size=3, padding=1),
            nn.BatchNorm2d(32),
            nn.ReLU(),
            nn.MaxPool2d(2),
            nn.Dropout2d(dropout_rate),
            
            # Third block
            nn.Conv2d(32, 64, kernel_size=3, padding=1),
            nn.BatchNorm2d(64),
            nn.ReLU(),
            nn.MaxPool2d(2),
            nn.Dropout2d(dropout_rate),
        )
        
        feature_size = 128 // (2 ** 3)  # 16x16 after 3 max pooling layers
        self.flat_features = 64 * feature_size * feature_size
        
        self.classifier = nn.Sequential(
            nn.Flatten(),
            nn.Linear(self.flat_features, 128),
            nn.BatchNorm1d(128),
            nn.ReLU(),
            nn.Dropout(dropout_rate),
            
            nn.Linear(128, 32),
            nn.BatchNorm1d(32),
            nn.ReLU(),
            nn.Dropout(dropout_rate),
            
            nn.Linear(32, 1),
            nn.Sigmoid()
        )
        
        self._initialize_weights()
    
    def _initialize_weights(self):
        for m in self.modules():
            if isinstance(m, nn.Conv2d):
                nn.init.kaiming_normal_(m.weight, mode='fan_out', nonlinearity='relu')
                if m.bias is not None:
                    nn.init.zeros_(m.bias)
            elif isinstance(m, (nn.BatchNorm2d, nn.BatchNorm1d)):
                nn.init.ones_(m.weight)
                nn.init.zeros_(m.bias)
            elif isinstance(m, nn.Linear):
                nn.init.kaiming_normal_(m.weight, mode='fan_out', nonlinearity='relu')
                nn.init.zeros_(m.bias)
    
    def forward(self, x):
        x = self.features(x)
        x = self.classifier(x)
        return x

def train_model(model, train_loader, val_loader, criterion, optimizer, scheduler, num_epochs, device, patience=20):
    best_val_loss = float('inf')
    best_epoch = 0
    patience_counter = 0
    train_losses, val_losses, train_accs, val_accs = [], [], [], []
    
    for epoch in range(num_epochs):
        # Training phase
        model.train()
        train_loss = 0
        train_correct = 0
        train_total = 0
        
        for images, labels in train_loader:
            images, labels = images.to(device), labels.to(device)
            
            optimizer.zero_grad()
            outputs = model(images)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()
            
            train_loss += loss.item()
            predicted = (outputs > 0.5).float()
            train_total += labels.size(0)
            train_correct += (predicted == labels).sum().item()
        
        train_loss = train_loss / len(train_loader)
        train_acc = train_correct / train_total
        
        # Validation phase
        model.eval()
        val_loss = 0
        val_correct = 0
        val_total = 0
        
        with torch.no_grad():
            for images, labels in val_loader:
                images, labels = images.to(device), labels.to(device)
                outputs = model(images)
                loss = criterion(outputs, labels)
                
                val_loss += loss.item()
                predicted = (outputs > 0.5).float()
                val_total += labels.size(0)
                val_correct += (predicted == labels).sum().item()
        
        val_loss = val_loss / len(val_loader)
        val_acc = val_correct / val_total
        
        train_losses.append(train_loss)
        val_losses.append(val_loss)
        train_accs.append(train_acc)
        val_accs.append(val_acc)
        
        print(f'Epoch [{epoch+1}/{num_epochs}]')
        print(f'Train Loss: {train_loss:.4f}, Train Acc: {train_acc:.4f}')
        print(f'Val Loss: {val_loss:.4f}, Val Acc: {val_acc:.4f}')
        
        scheduler.step(val_loss)
        
        if val_loss < best_val_loss:
            best_val_loss = val_loss
            best_epoch = epoch + 1
            # Save model with full path
            model_path = os.path.join('DyslexiaDetection', 'models', 'best_model.pth')
            torch.save({
                'epoch': epoch,
                'model_state_dict': model.state_dict(),
                'optimizer_state_dict': optimizer.state_dict(),
                'val_loss': val_loss,
                'val_acc': val_acc,
            }, model_path)
            patience_counter = 0
        else:
            patience_counter += 1
            if patience_counter >= patience:
                print(f'Early stopping triggered after {epoch + 1} epochs')
                print(f'Best model was saved at epoch {best_epoch}')
                break
    
    return train_losses, val_losses, train_accs, val_accs

def plot_training_history(train_losses, val_losses, train_accs, val_accs):
    """Plot training history"""
    # Create figure with two subplots
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 5))
    
    # Plot accuracy
    ax1.plot(train_accs, 'b-', label='Training Accuracy', linewidth=2)
    ax1.plot(val_accs, 'r--', label='Validation Accuracy', linewidth=2)
    ax1.set_title('Model Accuracy', fontsize=12, pad=10)
    ax1.set_xlabel('Epoch', fontsize=10)
    ax1.set_ylabel('Accuracy', fontsize=10)
    ax1.grid(True, linestyle='--', alpha=0.7)
    ax1.legend(fontsize=10)
    ax1.set_ylim([0, 1.1])
    
    # Plot loss
    ax2.plot(train_losses, 'b-', label='Training Loss', linewidth=2)
    ax2.plot(val_losses, 'r--', label='Validation Loss', linewidth=2)
    ax2.set_title('Model Loss', fontsize=12, pad=10)
    ax2.set_xlabel('Epoch', fontsize=10)
    ax2.set_ylabel('Loss', fontsize=10)
    ax2.grid(True, linestyle='--', alpha=0.7)
    ax2.legend(fontsize=10)
    
    # Adjust layout and save
    plt.tight_layout(pad=3.0)
    plt.savefig('training_history.png', dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()

def predict_image(model, image_path, device):
    """
    Predict if an image shows dyslexic handwriting
    """
    # Load and preprocess the image
    img = cv2.imread(str(image_path), cv2.IMREAD_GRAYSCALE)
    if img is None:
        raise ValueError(f"Could not load image at {image_path}")
    
    # Resize
    img = cv2.resize(img, (128, 128))
    
    # Normalize
    img = img.astype(np.float32) / 255.0
    
    # Apply CLAHE
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    img = clahe.apply(np.uint8(img * 255)).astype(np.float32) / 255.0
    
    # Apply Gaussian blur
    img = cv2.GaussianBlur(img, (3,3), 0)
    
    # Add batch and channel dimensions
    img = np.expand_dims(np.expand_dims(img, axis=0), axis=0)
    
    # Convert to tensor
    img_tensor = torch.FloatTensor(img).to(device)
    
    # Set model to evaluation mode
    model.eval()
    
    # Make prediction
    with torch.no_grad():
        output = model(img_tensor)
        probability = output.item()
        prediction = "Dyslexic" if probability > 0.5 else "Non-dyslexic"
        confidence = probability if probability > 0.5 else 1 - probability
    
    return prediction, confidence

def evaluate_model():
    """
    Load the best model and make predictions
    """
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model = DyslexiaCNN().to(device)
    
    # Load the best model with full path
    model_path = os.path.join('DyslexiaDetection', 'models', 'best_model.pth')
    checkpoint = torch.load(model_path)
    model.load_state_dict(checkpoint['model_state_dict'])
    print(f"Loaded model from epoch {checkpoint['epoch']+1}")
    print(f"Validation accuracy: {checkpoint['val_acc']:.4f}")
    
    # Create a directory for test results
    os.makedirs('test_results', exist_ok=True)
    
    while True:
        image_path = input("\nEnter the path to an image (or 'q' to quit): ")
        if image_path.lower() == 'q':
            break
        
        try:
            # Construct full path if relative path is provided
            if not os.path.isabs(image_path):
                image_path = os.path.join('DyslexiaDetection', image_path)
            
            prediction, confidence = predict_image(model, image_path, device)
            print(f"\nPrediction: {prediction}")
            print(f"Confidence: {confidence:.2%}")
        except Exception as e:
            print(f"Error processing image: {e}")

def main():
    # Set random seeds for reproducibility
    torch.manual_seed(42)
    np.random.seed(42)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False
    
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"Using device: {device}")
    
    # Create models directory with full path
    models_dir = os.path.join('DyslexiaDetection', 'models')
    os.makedirs(models_dir, exist_ok=True)
    
    print("Loading and preprocessing data...")
    X, y = load_and_preprocess_data()
    print(f"Dataset shape: {X.shape}")
    print(f"Number of samples: {len(y)}")
    print(f"Class distribution: Dyslexic: {sum(y)}, Non-dyslexic: {len(y) - sum(y)}")
    
    # Split with larger training set
    X_train, X_val, y_train, y_val = train_test_split(
        X, y, test_size=0.1, random_state=42, stratify=y
    )
    
    # Create datasets
    train_dataset = HandwritingDataset(X_train, y_train, is_training=True)
    val_dataset = HandwritingDataset(X_val, y_val, is_training=False)
    
    # Smaller batch size for better generalization
    train_loader = DataLoader(train_dataset, batch_size=4, shuffle=True, num_workers=0)
    val_loader = DataLoader(val_dataset, batch_size=4, num_workers=0)
    
    print("\nCreating model...")
    model = DyslexiaCNN().to(device)
    
    with open('model_summary.txt', 'w') as f:
        f.write(str(model))
    
    print("\nTraining model...")
    criterion = nn.BCELoss()
    optimizer = optim.AdamW(
        model.parameters(),
        lr=0.001,
        weight_decay=0.0001
    )
    scheduler = optim.lr_scheduler.ReduceLROnPlateau(
        optimizer,
        mode='min',
        factor=0.5,
        patience=10,
        min_lr=1e-6
    )
    train_losses, val_losses, train_accs, val_accs = train_model(
        model, train_loader, val_loader, criterion, optimizer, scheduler, 200, device
    )
    
    print("\nSaving training history...")
    plot_training_history(train_losses, val_losses, train_accs, val_accs)
    
    print("\nSaving final model...")
    torch.save({
        'model_state_dict': model.state_dict(),
        'train_losses': train_losses,
        'val_losses': val_losses,
        'train_accs': train_accs,
        'val_accs': val_accs,
    }, os.path.join(models_dir, 'final_model.pth'))
    
    print("\nTraining completed!")

if __name__ == "__main__":
    main()
    
    # Ask if user wants to evaluate images
    response = input("\nWould you like to evaluate individual images? (y/n): ")
    if response.lower() == 'y':
        evaluate_model() 