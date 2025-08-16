"""Core utility functions"""

import numpy as np
from typing import List, Optional
from PIL import Image
import io
import base64
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.conf import settings


def cosine_similarity(embedding1: List[float], embedding2: List[float]) -> float:
    """Calculate cosine similarity between two embeddings"""
    if not embedding1 or not embedding2:
        return 0.0

    vec1 = np.array(embedding1)
    vec2 = np.array(embedding2)

    dot_product = np.dot(vec1, vec2)
    norm1 = np.linalg.norm(vec1)
    norm2 = np.linalg.norm(vec2)

    if norm1 == 0 or norm2 == 0:
        return 0.0

    return dot_product / (norm1 * norm2)


def generate_face_embedding(image_data: bytes) -> Optional[List[float]]:
    """
    Generate face embedding from image data
    This is a placeholder - integrate with your preferred face recognition model
    """
    # Placeholder implementation - replace with actual face recognition model
    # Example: using face_recognition library or MediaPipe
    try:
        # Convert bytes to PIL Image
        image = Image.open(io.BytesIO(image_data))

        # Placeholder: return random embedding for demo
        # In production, use actual face recognition model
        embedding = np.random.rand(512).tolist()
        return embedding
    except Exception as e:
        print(f"Error generating embedding: {e}")
        return None


def validate_image_similarity(
    new_embeddings: List[List[float]], stored_embeddings: List[List[float]]
) -> bool:
    """
    Validate if new image embeddings match stored login embeddings
    Returns True if similarity is above threshold
    """
    if not new_embeddings or not stored_embeddings:
        return False

    max_similarity = 0.0

    for new_emb in new_embeddings:
        for stored_emb in stored_embeddings:
            similarity = cosine_similarity(new_emb, stored_emb)
            max_similarity = max(max_similarity, similarity)

    return max_similarity >= settings.SIMILARITY_THRESHOLD


def process_uploaded_image(
    uploaded_file: InMemoryUploadedFile,
) -> Optional[List[float]]:
    """Process uploaded image and return embedding"""
    try:
        image_data = uploaded_file.read()
        return generate_face_embedding(image_data)
    except Exception as e:
        print(f"Error processing uploaded image: {e}")
        return None


def base64_to_embedding(base64_image: str) -> Optional[List[float]]:
    """Convert base64 image to embedding"""
    try:
        # Remove data URL prefix if present
        if "," in base64_image:
            base64_image = base64_image.split(",")[1]

        image_data = base64.b64decode(base64_image)
        return generate_face_embedding(image_data)
    except Exception as e:
        print(f"Error converting base64 to embedding: {e}")
        return None
