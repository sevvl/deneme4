from PIL import Image
import io
import base64

def image_to_bytes(image: Image.Image, format: str = "JPEG") -> bytes:
    """
    Converts a PIL Image object to bytes.
    """
    img_byte_arr = io.BytesIO()
    image.save(img_byte_arr, format=format)
    return img_byte_arr.getvalue()

def bytes_to_image(image_bytes: bytes) -> Image.Image:
    """
    Converts bytes to a PIL Image object.
    """
    return Image.open(io.BytesIO(image_bytes))

def get_image_dimensions(image_bytes: bytes) -> tuple[int, int]:
    """
    Returns the width and height of an image in bytes.
    """
    img = Image.open(io.BytesIO(image_bytes))
    return img.width, img.height

def encode_image_to_base64(image_bytes: bytes) -> str:
    """
    Encodes image bytes to a base64 string.
    """
    return base64.b64encode(image_bytes).decode('utf-8')

def decode_image_from_base64(base64_string: str) -> bytes:
    """
    Decodes a base64 string to image bytes.
    """
    return base64.b64decode(base64_string)

