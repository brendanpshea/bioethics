import numpy as np
from PIL import Image, ImageOps, ImageFilter, ImageEnhance, ImageChops

def process_to_sketch(input_path, output_path):
    img = Image.open(input_path)
    
    # 1. Standardize aspect ratio to 1:1 with white padding (800x800)
    img.thumbnail((800, 800), Image.Resampling.LANCZOS)
    square_img = Image.new("RGB", (800, 800), (255, 255, 255))
    offset = ((800 - img.width) // 2, (800 - img.height) // 2)
    square_img.paste(img, offset)
    
    # 2. Convert to grayscale and invert for blur
    gray = square_img.convert('L')
    inverted = ImageOps.invert(gray)
    
    # 3. Apply strong Gaussian blur
    blurred = inverted.filter(ImageFilter.GaussianBlur(radius=8))
    
    # 4. Color Dodge blend to isolate strong edges / outline sketches
    g = np.array(gray, dtype=float)
    b = np.array(blurred, dtype=float)
    dodge = g * 255.0 / (255.0 - b + 1.0)
    dodge = np.clip(dodge, 0, 255).astype(np.uint8)
    
    sketch = Image.fromarray(dodge)
    
    # 5. Boost contrast of lines to make them look like sharp ink pen strokes
    enhancer = ImageEnhance.Contrast(sketch)
    ink_lines = enhancer.enhance(3.0) # High contrast ink strokes
    
    # 6. Apply a soft duotone color wash using the course palette:
    # We want a warm cream background (#f7f5f0) with subtle amber/teal tone.
    # We can colorize the grayscale outline slightly or use a textured color wash.
    wash = Image.new("RGB", (800, 800), (248, 245, 238)) # Beautiful warm cream paper base
    
    # Let's blend in a soft teal watercolor vignette
    # We can create a radial gradient or just a soft flat tint for absolute cleanliness.
    # To keep it premium, let's keep the background as clean, warm paper, which matches slide.scss perfectly!
    
    # 7. Perform proper Multiply blend: Ink lines multiply over the cream paper background
    final_img = ImageChops.multiply(wash, ink_lines.convert("RGB"))
    
    # 8. Save
    final_img.save(output_path, "PNG")
    print(f"Bespoke sketch generated: {output_path}")

if __name__ == "__main__":
    process_to_sketch("images/kant.jpg", "assets/images/kant.png")
    process_to_sketch("images/mill.jpg", "assets/images/mill.png")
    process_to_sketch("images/bentham.jpg", "assets/images/bentham.png")
    process_to_sketch("images/aristotle.jpg", "assets/images/aristotle.png")
