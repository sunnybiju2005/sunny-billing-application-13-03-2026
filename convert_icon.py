from PIL import Image
import os

def convert_to_ico(image_path, output_path):
    img = Image.open(image_path)
    # Resize to common icon sizes
    icon_sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
    img.save(output_path, sizes=icon_sizes)
    print(f"Icon saved successfully at {output_path}")

if __name__ == "__main__":
    # The path to the generated image
    source_img = r"C:\Users\sunny\.gemini\antigravity\brain\30fa1fb6-808c-4465-954b-7948b3d57cdf\drop_logo_icon_1773417836415.png"
    target_ico = r"c:\sunny\github\repositery\sunny-billing-application-13-03-2026\app_icon.ico"
    convert_to_ico(source_img, target_ico)
