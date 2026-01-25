"""
ASCII Art Converter - Converts images to ASCII art with color support
Enhanced with debugging features
"""
import numpy as np
from PIL import Image
import sys


class AsciiConverter:
    """Converts images to ASCII art with color support."""
    
    # ASCII characters from light to dark
    ASCII_CHARS_SIMPLE = " .:-=+*#%@"
    ASCII_CHARS_DETAILED = " .'`^\",:;Il!i><~+_-?][}{1)(|\\/tfjrxnuvczXYUJCLQ0OZmwqpdbkhao*#MW&8%B@$"
    
    def __init__(self, width=100, char_set="simple", color_mode="rainbow", debug=False):
        """
        Initialize ASCII converter.
        
        Args:
            width: Target width in characters
            char_set: "simple" or "detailed" character set
            color_mode: "rainbow", "bw" (black/white), or "normal" (original colors)
            debug: Enable debug output
        """
        self.width = width
        self.color_mode = color_mode
        self.debug = debug
        
        if char_set == "simple":
            self.chars = self.ASCII_CHARS_SIMPLE
        else:
            self.chars = self.ASCII_CHARS_DETAILED
            
        self.char_count = len(self.chars)
        
        if self.debug:
            print(f"[DEBUG] AsciiConverter initialized:", file=sys.stderr)
            print(f"  Width: {self.width}", file=sys.stderr)
            print(f"  Color mode: {self.color_mode}", file=sys.stderr)
            print(f"  Char set: {self.chars}", file=sys.stderr)
    
    def _get_rainbow_color(self, brightness):
        """
        Get rainbow heatmap color based on brightness (0-255).
        Returns RGB tuple.
        
        Heatmap: Blue -> Cyan -> Green -> Yellow -> Red
        """
        # Normalize to 0-1
        normalized = brightness / 255.0
        
        if normalized < 0.25:
            # Blue to Cyan
            r = 0
            g = int(normalized * 4 * 255)
            b = 255
        elif normalized < 0.5:
            # Cyan to Green
            r = 0
            g = 255
            b = int((0.5 - normalized) * 4 * 255)
        elif normalized < 0.75:
            # Green to Yellow
            r = int((normalized - 0.5) * 4 * 255)
            g = 255
            b = 0
        else:
            # Yellow to Red
            r = 255
            g = int((1.0 - normalized) * 4 * 255)
            b = 0
        
        return (r, g, b)
    
    def image_to_ascii(self, image):
        """
        Convert a PIL Image or numpy array to ASCII art.
        Maintains original resolution as much as possible.
        
        Args:
            image: PIL Image or numpy array (BGR or RGB)
            
        Returns:
            String containing ASCII art with newlines (with ANSI color codes if color_mode != 'bw')
        """
        try:
            # Convert to PIL Image if numpy array
            if isinstance(image, np.ndarray):
                if self.debug:
                    print(f"[DEBUG] Input is numpy array: {image.shape}", file=sys.stderr)
                
                # OpenCV uses BGR, convert to RGB
                if len(image.shape) == 3 and image.shape[2] == 3:
                    image_rgb = image[:, :, ::-1]
                    image_color = Image.fromarray(image_rgb)
                    image = Image.fromarray(image_rgb)
                else:
                    image_color = Image.fromarray(image)
                    image = Image.fromarray(image)
            else:
                if self.debug:
                    print(f"[DEBUG] Input is PIL Image: {image.size}", file=sys.stderr)
                image_color = image.copy()
            
            # Calculate height to maintain original image aspect ratio
            # AND account for terminal character aspect ratio
            original_width, original_height = image.size
            
            # Terminal characters are roughly 2:1 (height:width)
            # So we need to compensate when converting pixels to characters
            char_aspect = 0.5  # Characters are twice as tall as wide
            
            # Calculate target dimensions
            target_width = self.width
            # Preserve original image aspect ratio while accounting for char aspect
            target_height = int((original_height / original_width) * target_width * char_aspect)
            
            if self.debug:
                print(f"[DEBUG] Original: {original_width}x{original_height}", file=sys.stderr)
                print(f"[DEBUG] Target: {target_width}x{target_height} chars", file=sys.stderr)
            
            # Resize image to target resolution
            image = image.resize((target_width, target_height), Image.Resampling.LANCZOS)
            image_color = image_color.resize((target_width, target_height), Image.Resampling.LANCZOS)
            
            # Convert to grayscale for character selection
            image_gray = image.convert('L')
            pixels_gray = np.array(image_gray)
            
            # Get color information if needed
            if self.color_mode != 'bw':
                pixels_color = np.array(image_color.convert('RGB'))
                if self.debug:
                    print(f"[DEBUG] Color array shape: {pixels_color.shape}", file=sys.stderr)
            
            # Map pixel values (0-255) to character indices
            normalized = pixels_gray / 255.0
            char_indices = (normalized * (self.char_count - 1)).astype(int)
            
            # Build ASCII string with colors
            ascii_lines = []
            for y in range(target_height):
                line_chars = []
                for x in range(target_width):
                    char = self.chars[char_indices[y, x]]
                    
                    if self.color_mode == 'bw':
                        # Black and white - no color codes
                        line_chars.append(char)
                    elif self.color_mode == 'rainbow':
                        # Rainbow heatmap based on brightness
                        brightness = pixels_gray[y, x]
                        r, g, b = self._get_rainbow_color(brightness)
                        # ANSI 24-bit color escape code
                        color_code = f'\033[38;2;{r};{g};{b}m'
                        line_chars.append(f'{color_code}{char}')
                    elif self.color_mode == 'normal':
                        # Original image colors
                        r, g, b = pixels_color[y, x]
                        color_code = f'\033[38;2;{r};{g};{b}m'
                        line_chars.append(f'{color_code}{char}')
                
                # Add reset code at end of line if using colors
                if self.color_mode != 'bw':
                    line_chars.append('\033[0m')
                
                ascii_lines.append(''.join(line_chars))
            
            if self.debug:
                print(f"[DEBUG] Generated {len(ascii_lines)} lines of ASCII", file=sys.stderr)
                if ascii_lines:
                    print(f"[DEBUG] First line length: {len(ascii_lines[0])} chars", file=sys.stderr)
            
            return '\n'.join(ascii_lines)
            
        except Exception as e:
            print(f"[ERROR] image_to_ascii failed: {e}", file=sys.stderr)
            import traceback
            traceback.print_exc(file=sys.stderr)
            # Return error message as ASCII
            return f"ERROR: {str(e)}"
    
    def set_width(self, width):
        """Update the target width for ASCII conversion."""
        self.width = width
        if self.debug:
            print(f"[DEBUG] Width updated to {width}", file=sys.stderr)
    
    def generate_no_cam_placeholder(self):
        """Generate a 'No Cam' placeholder ASCII art."""
        lines = []
        width = self.width
        height = max(10, width // 3)
        
        # Create border
        border = "═" * width
        lines.append(border)
        
        # Add some padding
        lines.append("║" + " " * (width - 2) + "║")
        
        # Center the "No Cam" message
        message = "NO CAM"
        padding = (width - len(message) - 2) // 2
        line = "║" + " " * padding + message + " " * (width - len(message) - padding - 2) + "║"
        lines.append(line)
        
        # Add more padding
        for _ in range(height - 4):
            lines.append("║" + " " * (width - 2) + "║")
        
        # Bottom border
        lines.append(border)
        
        return "\n".join(lines)
    
    def set_color_mode(self, mode):
        """Update color mode: 'rainbow', 'bw', or 'normal'."""
        if mode in ['rainbow', 'bw', 'normal']:
            self.color_mode = mode
            if self.debug:
                print(f"[DEBUG] Color mode changed to {mode}", file=sys.stderr)
        else:
            print(f"[ERROR] Invalid color mode: {mode}", file=sys.stderr)


if __name__ == "__main__":
    # Test the converter with a sample image
    print("Testing ASCII Converter with Color Modes...")
    print("=" * 70)
    
    # Create a test gradient image
    test_img = Image.new('RGB', (256, 128))
    pixels = np.array(test_img)
    
    # Create horizontal gradient with colors
    for y in range(128):
        for x in range(256):
            pixels[y, x] = [x, 128, 255 - x]
    
    test_img = Image.fromarray(pixels.astype('uint8'))
    
    # Test different color modes
    for mode in ['bw', 'rainbow', 'normal']:
        print(f"\n{'='*70}")
        print(f"Color Mode: {mode.upper()}")
        print('='*70)
        
        converter = AsciiConverter(width=60, char_set="simple", aspect_ratio=0.25, 
                                   color_mode=mode, debug=True)
        ascii_art = converter.image_to_ascii(test_img)
        
        # Show result
        lines = ascii_art.split('\n')
        print(f"\nGenerated {len(lines)} lines")
        print("\nFirst 5 lines:")
        for i, line in enumerate(lines[:5]):
            print(f"  {i+1}: {line}")
        
        print(f"\nCharacter set: {converter.chars}")
        print(f"Aspect ratio: {converter.aspect_ratio} (double line density)")
    
    print("\n" + "="*70)
    print("Test complete! If you see colorful gradients above, colors work!")
    print("If not, your terminal may not support 24-bit color (use --color bw)")
