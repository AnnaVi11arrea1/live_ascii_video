"""
ASCII Art Converter - Converts images to ASCII art representation
"""
import numpy as np
from PIL import Image
from rich import print
from rich.highlighter import Highlighter
from random import randint

class RainbowHighlighter(Highlighter):
    def highlight(self, text):
        for index in range(len(text)):
            text.stylize(f"color({randint(16, 255)})", index, index + 1)


rainbow = RainbowHighlighter()


class AsciiConverter:
    """Converts images to ASCII art."""
    
    # ASCII characters from light to dark
    ASCII_CHARS_SIMPLE = " .:-=+*#%@"
    ASCII_CHARS_DETAILED = " .'`^\",:;Il!i><~+_-?][}{1)(|\\/tfjrxnuvczXYUJCLQ0OZmwqpdbkhao*#MW&8%B@$"
    
    def __init__(self, width=100, char_set="simple", aspect_ratio=0.55):
        """
        Initialize ASCII converter.
        
        Args:
            width: Target width in characters
            char_set: "simple" or "detailed" character set
            aspect_ratio: Character height/width ratio (0.55 is typical for terminal fonts)
        """
        self.width = width
        self.aspect_ratio = aspect_ratio
        
        if char_set == "simple":
            self.chars = self.ASCII_CHARS_SIMPLE
        else:
            self.chars = self.ASCII_CHARS_DETAILED
            
        self.char_count = len(self.chars)
    
    def image_to_ascii(self, image):
        """
        Convert a PIL Image or numpy array to ASCII art.
        
        Args:
            image: PIL Image or numpy array (BGR or RGB)
            
        Returns:
            String containing ASCII art with newlines
        """
        # Convert to PIL Image if numpy array
        if isinstance(image, np.ndarray):
            # OpenCV uses BGR, convert to RGB
            if len(image.shape) == 3 and image.shape[2] == 3:
                image = Image.fromarray(image[:, :, ::-1])
            else:
                image = Image.fromarray(image)
        
        # Calculate height maintaining aspect ratio
        original_width, original_height = image.size
        height = int(self.width * original_height / original_width * self.aspect_ratio)
        
        # Resize image
        image = image.resize((self.width, height), Image.Resampling.LANCZOS)
        
        # Convert to grayscale
        image = image.convert('L')
        
        # Convert to numpy array
        pixels = np.array(image)
        
        # Map pixel values (0-255) to character indices
        # Normalize to 0-1, then scale to char count range
        normalized = pixels / 255.0
        char_indices = (normalized * (self.char_count - 1)).astype(int)
        
        # Build ASCII string
        ascii_lines = []
        for row in char_indices:
            ascii_line = ''.join(self.chars[idx] for idx in row)
            ascii_lines.append(ascii_line)



        
        return '\n'.join(ascii_lines)


    
    def set_width(self, width):
        """Update the target width for ASCII conversion."""
        self.width = width


if __name__ == "__main__":
    # Test the converter with a sample image
    print("Testing ASCII Converter...")
    
    # Create a test gradient image
    test_img = Image.new('L', (256, 128))
    pixels = np.array(test_img)
    
    # Create horizontal gradient
    for i in range(128):
        pixels[i, :] = np.linspace(0, 255, 256)
    
    test_img = Image.fromarray(pixels)
    
    # Convert to ASCII
    converter = AsciiConverter(width=80, char_set="simple")
    ascii_art = converter.image_to_ascii(test_img)
    
    
    print("\nHorizontal Gradient Test:")
    print(ascii_art)
    print(f"\nUsing character set: {converter.chars}")
