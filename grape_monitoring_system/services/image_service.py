import os
from PIL import Image
import io

class ImageService:
    def __init__(self):
        self.upload_dir = "grape_monitoring_system/data/uploads"
        os.makedirs(self.upload_dir, exist_ok=True)

    def save_image(self, image_data: bytes, filename: str) -> str:
        """
        Saves image data to the uploads directory.
        Returns the path to the saved image.
        """
        filepath = os.path.join(self.upload_dir, filename)
        with open(filepath, "wb") as f:
            f.write(image_data)
        return filepath

    def get_image_bytes(self, image_path: str) -> bytes:
        """
        Reads image from a given path and returns its bytes.
        """
        with open(image_path, "rb") as f:
            return f.read()

    def resize_image(self, image_data: bytes, max_size=(1024, 1024)) -> bytes:
        """
        Resizes an image if it exceeds max_size, maintaining aspect ratio.
        Returns the resized image as bytes.
        """
        try:
            image = Image.open(io.BytesIO(image_data))
            image.thumbnail(max_size, Image.Resampling.LANCZOS)
            output_buffer = io.BytesIO()
            image.save(output_buffer, format=image.format)
            return output_buffer.getvalue()
        except Exception as e:
            print(f"Error resizing image: {e}")
            return image_data # Return original if resize fails

    def convert_to_jpeg(self, image_data: bytes) -> bytes:
        """
        Converts an image to JPEG format if it's not already, and returns its bytes.
        """
        try:
            image = Image.open(io.BytesIO(image_data))
            if image.format != 'JPEG':
                # Convert RGBA to RGB if necessary, as JPEG does not support alpha channel
                if image.mode == 'RGBA':
                    image = image.convert('RGB')
                output_buffer = io.BytesIO()
                image.save(output_buffer, format='JPEG')
                return output_buffer.getvalue()
            return image_data
        except Exception as e:
            print(f"Error converting image to JPEG: {e}")
            return image_data # Return original if conversion fails

