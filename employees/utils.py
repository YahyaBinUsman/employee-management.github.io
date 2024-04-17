# utils.py
import base64
import face_recognition

def get_face_encoding(image_path):
    try:
        image = face_recognition.load_image_file(image_path)
        face_encoding = face_recognition.face_encodings(image)[0]
        return face_encoding.tolist()
    except Exception as e:
        print(f"Error encoding face: {e}")
        return None
import base64
import struct

def base64_to_float_list(base64_str):
    try:
        # Add padding to the base64 string if needed
        padding_needed = len(base64_str) % 4
        if padding_needed > 0:
            base64_str += '=' * (4 - padding_needed)

        # Decode base64 string
        decoded_bytes = base64.b64decode(base64_str)

        # Ensure the length is a multiple of 4 (size of float)
        if len(decoded_bytes) % 4 != 0:
            # Pad the decoded bytes to make it a multiple of 4
            padding_size = 4 - len(decoded_bytes) % 4
            decoded_bytes += b'\x00' * padding_size

        # Use struct to interpret bytes as float values
        float_list = struct.unpack(f'{len(decoded_bytes)//4}f', decoded_bytes)

        return list(float_list)
    except Exception as e:
        print(f"Error decoding base64 string: {e}")
        return []

