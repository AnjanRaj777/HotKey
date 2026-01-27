from PIL import Image
import os

def convert_to_ico():
    img_path = r"assets/logo.png"
    ico_path = r"assets/logo.ico"
    
    if not os.path.exists(img_path):
        print("Logo not found")
        return

    img = Image.open(img_path)
    img.save(ico_path, format='ICO', sizes=[(256, 256)])
    print(f"Converted {img_path} to {ico_path}")

if __name__ == "__main__":
    convert_to_ico()
