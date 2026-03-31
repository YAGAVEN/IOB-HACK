"""
GAN (Generative Adversarial Network) for HYDRA Module
Adversarial pattern generation and detection for money laundering schemes
"""

import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
from typing import Dict, List, Tuple
from datetime import datetime
import random

class Generator(nn.Module):
    """
    Generator network for creating adversarial transaction patterns
    """
    
    def __init__(self, latent_dim=100, output_dim=50):
        super(Generator, self).__init__()
        
        self.model = nn.Sequential(
            nn.Linear(latent_dim, 256),
            nn.BatchNorm1d(256),
            nn.LeakyReLU(0.2),
            nn.Dropout(0.3),
            
            nn.Linear(256, 512),
            nn.BatchNorm1d(512),
            nn.LeakyReLU(0.2),
            nn.Dropout(0.3),
            
            nn.Linear(512, 256),
            nn.BatchNorm1d(256),
            nn.LeakyReLU(0.2),
            nn.Dropout(0.3),
            
            nn.Linear(256, output_dim),
            nn.Tanh()
        )
    
    def forward(self, z):
        return self.model(z)

class Discriminator(nn.Module):
    """
    Discriminator network for detecting real vs generated patterns
    """
    
    def __init__(self, input_dim=50):
        super(Discriminator, self).__init__()
        
        self.model = nn.Sequential(
            nn.Linear(input_dim, 256),
            nn.LeakyReLU(0.2),
            nn.Dropout(0.3),
            
            nn.Linear(256, 128),
            nn.LeakyReLU(0.2),
            nn.Dropout(0.3),
            
            nn.Linear(128, 64),
            nn.LeakyReLU(0.2),
            nn.Dropout(0.3),
            
            nn.Linear(64, 1),
            nn.Sigmoid()
        )
    
    def forward(self, x):
        return self.model(x)

class HYDRA_GAN:
    """
    HYDRA GAN System for adversarial money laundering pattern generation
    """
    
    def __init__(self, latent_dim=100, pattern_dim=50, device='cpu'):
        """
        Initialize HYDRA GAN
        
        Args:
            latent_dim: Dimension of latent noise vector
            pattern_dim: Dimension of transaction pattern features
            device: 'cpu' or 'cuda'
        """
        self.device = torch.device(device if torch.cuda.is_available() else 'cpu')
        self.latent_dim = latent_dim
        self.pattern_dim = pattern_dim
        
        # Initialize networks
        self.generator = Generator(latent_dim, pattern_dim).to(self.device)
        self.discriminator = Discriminator(pattern_dim).to(self.device)
        
        # Optimizers
        self.g_optimizer = optim.Adam(self.generator.parameters(), lr=0.0002, betas=(0.5, 0.999))
        self.d_optimizer = optim.Adam(self.discriminator.parameters(), lr=0.0002, betas=(0.5, 0.999))
        
        # Loss function
        self.criterion = nn.BCELoss()
        
        # Training metrics
        self.is_trained = False
        self.training_history = {
            'g_losses': [],
            'd_losses': [],
            'epochs': 0
        }
        
        # Pattern types
        self.pattern_types = [
            'smurfing_enhanced',
            'layering_complex',
            'integration_hidden',
            'shell_company_web',
            'trade_based_ml',
            'crypto_mixing',
            'invoice_manipulation',
            'real_estate_scheme'
        ]
    
    def train(self, real_patterns, epochs=100, batch_size=32):
        """
        Train the GAN on real money laundering patterns
        
        Args:
            real_patterns: Real transaction patterns (numpy array or tensor)
            epochs: Number of training epochs
            batch_size: Batch size for training
            
        Returns:
            training_history: Dictionary with training metrics
        """
        if isinstance(real_patterns, np.ndarray):
            real_patterns = torch.FloatTensor(real_patterns).to(self.device)
        
        n_samples = real_patterns.shape[0]
        
        for epoch in range(epochs):
            epoch_g_loss = 0
            epoch_d_loss = 0
            n_batches = 0
            
            # Shuffle data
            indices = torch.randperm(n_samples)
            
            for i in range(0, n_samples, batch_size):
                batch_indices = indices[i:min(i+batch_size, n_samples)]
                real_batch = real_patterns[batch_indices]
                current_batch_size = real_batch.shape[0]
                
                # Train Discriminator
                self.d_optimizer.zero_grad()
                
                # Real patterns
                real_labels = torch.ones(current_batch_size, 1).to(self.device)
                real_output = self.discriminator(real_batch)
                d_loss_real = self.criterion(real_output, real_labels)
                
                # Fake patterns
                noise = torch.randn(current_batch_size, self.latent_dim).to(self.device)
                fake_patterns = self.generator(noise)
                fake_labels = torch.zeros(current_batch_size, 1).to(self.device)
                fake_output = self.discriminator(fake_patterns.detach())
                d_loss_fake = self.criterion(fake_output, fake_labels)
                
                # Total discriminator loss
                d_loss = d_loss_real + d_loss_fake
                d_loss.backward()
                self.d_optimizer.step()
                
                # Train Generator
                self.g_optimizer.zero_grad()
                
                noise = torch.randn(current_batch_size, self.latent_dim).to(self.device)
                fake_patterns = self.generator(noise)
                fake_output = self.discriminator(fake_patterns)
                g_loss = self.criterion(fake_output, real_labels)  # Want discriminator to think fake is real
                
                g_loss.backward()
                self.g_optimizer.step()
                
                epoch_g_loss += g_loss.item()
                epoch_d_loss += d_loss.item()
                n_batches += 1
            
            # Record epoch metrics
            avg_g_loss = epoch_g_loss / n_batches
            avg_d_loss = epoch_d_loss / n_batches
            
            self.training_history['g_losses'].append(avg_g_loss)
            self.training_history['d_losses'].append(avg_d_loss)
            self.training_history['epochs'] += 1
            
            if (epoch + 1) % 10 == 0:
                print(f"Epoch [{epoch+1}/{epochs}] - D Loss: {avg_d_loss:.4f}, G Loss: {avg_g_loss:.4f}")
        
        self.is_trained = True
        return self.training_history
    
    def generate_adversarial_pattern(self, n_samples=1, pattern_type=None):
        """
        Generate adversarial transaction patterns
        
        Args:
            n_samples: Number of patterns to generate
            pattern_type: Optional specific pattern type
            
        Returns:
            patterns: Generated adversarial patterns
        """
        self.generator.eval()
        
        with torch.no_grad():
            noise = torch.randn(n_samples, self.latent_dim).to(self.device)
            generated_patterns = self.generator(noise)
            patterns = generated_patterns.cpu().numpy()
        
        # Convert to interpretable pattern structure
        result_patterns = []
        for i in range(n_samples):
            pattern = self._interpret_pattern(patterns[i], pattern_type)
            result_patterns.append(pattern)
        
        return result_patterns if n_samples > 1 else result_patterns[0]
    
    def _interpret_pattern(self, pattern_vector, pattern_type=None):
        """
        Convert pattern vector to interpretable transaction pattern
        
        Args:
            pattern_vector: Raw pattern vector from generator
            pattern_type: Optional pattern type label
            
        Returns:
            pattern: Dictionary with pattern details
        """
        if pattern_type is None:
            pattern_type = random.choice(self.pattern_types)
        
        # Normalize pattern features
        pattern_normalized = (pattern_vector + 1) / 2  # From [-1, 1] to [0, 1]
        
        pattern = {
            'pattern_id': f'GAN_{datetime.now().strftime("%Y%m%d_%H%M%S")}_{random.randint(1000, 9999)}',
            'pattern_type': pattern_type,
            'complexity_score': float(pattern_normalized[:10].mean()),
            'features': {
                'transaction_count': int(pattern_normalized[0] * 50 + 10),
                'total_amount': float(pattern_normalized[1] * 500000 + 50000),
                'hop_count': int(pattern_normalized[2] * 8 + 1),
                'account_diversity': float(pattern_normalized[3]),
                'temporal_spread_hours': float(pattern_normalized[4] * 168),  # Up to 7 days
                'structuring_likelihood': float(pattern_normalized[5]),
                'circular_flow': float(pattern_normalized[6]),
                'international_hops': int(pattern_normalized[7] * 5),
                'shell_company_involvement': float(pattern_normalized[8]),
                'crypto_mixing': float(pattern_normalized[9])
            },
            'raw_vector': pattern_vector.tolist(),
            'generated_at': datetime.now().isoformat()
        }
        
        return pattern
    
    def detect_pattern(self, pattern_vector):
        """
        Detect if a pattern is likely adversarial
        
        Args:
            pattern_vector: Transaction pattern vector
            
        Returns:
            detection_result: Dictionary with detection results
        """
        self.discriminator.eval()
        
        if isinstance(pattern_vector, np.ndarray):
            pattern_vector = torch.FloatTensor(pattern_vector).to(self.device)
        
        if len(pattern_vector.shape) == 1:
            pattern_vector = pattern_vector.unsqueeze(0)
        
        with torch.no_grad():
            detection_score = self.discriminator(pattern_vector)
            score = float(detection_score[0])
        
        return {
            'is_adversarial': score < 0.5,  # Low score = likely generated
            'confidence': abs(score - 0.5) * 2,  # Distance from decision boundary
            'detection_score': score,
            'detected_at': datetime.now().isoformat()
        }
    
    def test_detection_accuracy(self, real_patterns, n_generated=100):
        """
        Test detection accuracy on real vs generated patterns
        
        Args:
            real_patterns: Real transaction patterns
            n_generated: Number of fake patterns to generate
            
        Returns:
            metrics: Accuracy metrics
        """
        # Generate fake patterns
        fake_patterns = []
        for _ in range(n_generated // 10):
            noise = torch.randn(10, self.latent_dim).to(self.device)
            generated = self.generator(noise)
            fake_patterns.append(generated)
        fake_patterns = torch.cat(fake_patterns, dim=0)
        
        # Test on real patterns
        real_tensor = torch.FloatTensor(real_patterns[:n_generated]).to(self.device)
        real_preds = self.discriminator(real_tensor)
        real_accuracy = (real_preds > 0.5).float().mean().item()
        
        # Test on fake patterns
        fake_preds = self.discriminator(fake_patterns)
        fake_accuracy = (fake_preds <= 0.5).float().mean().item()
        
        overall_accuracy = (real_accuracy + fake_accuracy) / 2
        
        return {
            'overall_accuracy': overall_accuracy,
            'real_detection_rate': real_accuracy,
            'fake_detection_rate': fake_accuracy,
            'n_real_tested': n_generated,
            'n_fake_tested': n_generated
        }
    
    def save_model(self, filepath):
        """Save trained GAN models"""
        torch.save({
            'generator_state_dict': self.generator.state_dict(),
            'discriminator_state_dict': self.discriminator.state_dict(),
            'g_optimizer_state_dict': self.g_optimizer.state_dict(),
            'd_optimizer_state_dict': self.d_optimizer.state_dict(),
            'training_history': self.training_history,
            'latent_dim': self.latent_dim,
            'pattern_dim': self.pattern_dim,
            'is_trained': self.is_trained
        }, filepath)
        print(f"Model saved to {filepath}")
    
    def load_model(self, filepath):
        """Load trained GAN models"""
        checkpoint = torch.load(filepath, map_location=self.device)
        
        self.generator.load_state_dict(checkpoint['generator_state_dict'])
        self.discriminator.load_state_dict(checkpoint['discriminator_state_dict'])
        self.g_optimizer.load_state_dict(checkpoint['g_optimizer_state_dict'])
        self.d_optimizer.load_state_dict(checkpoint['d_optimizer_state_dict'])
        self.training_history = checkpoint['training_history']
        self.is_trained = checkpoint['is_trained']
        
        print(f"Model loaded from {filepath}")


if __name__ == "__main__":
    print("HYDRA GAN System Test\n")
    
    # Initialize GAN
    gan = HYDRA_GAN(latent_dim=100, pattern_dim=50, device='cpu')
    
    # Generate synthetic training data
    n_real_patterns = 1000
    real_patterns = np.random.randn(n_real_patterns, 50) * 0.5
    
    print(f"Training on {n_real_patterns} real patterns...")
    history = gan.train(real_patterns, epochs=50, batch_size=32)
    
    print(f"\nTraining complete. Final losses:")
    print(f"  Generator: {history['g_losses'][-1]:.4f}")
    print(f"  Discriminator: {history['d_losses'][-1]:.4f}")
    
    # Generate adversarial patterns
    print("\nGenerating adversarial patterns...")
    adversarial_pattern = gan.generate_adversarial_pattern(n_samples=1)
    
    print(f"\nGenerated Pattern:")
    print(f"  ID: {adversarial_pattern['pattern_id']}")
    print(f"  Type: {adversarial_pattern['pattern_type']}")
    print(f"  Complexity: {adversarial_pattern['complexity_score']:.3f}")
    print(f"  Transaction Count: {adversarial_pattern['features']['transaction_count']}")
    print(f"  Total Amount: ${adversarial_pattern['features']['total_amount']:,.2f}")
    
    # Test detection
    print("\nTesting detection accuracy...")
    metrics = gan.test_detection_accuracy(real_patterns, n_generated=100)
    print(f"  Overall Accuracy: {metrics['overall_accuracy']:.3f}")
    print(f"  Real Detection Rate: {metrics['real_detection_rate']:.3f}")
    print(f"  Fake Detection Rate: {metrics['fake_detection_rate']:.3f}")
