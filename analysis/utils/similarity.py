import numpy as np
from skimage import metrics
from sklearn.metrics.pairwise import cosine_similarity
from PIL import Image
import imagehash


def calculate_cosine_similarity(vec_a, vec_b):
    vec_a = vec_a.reshape(1, -1)
    vec_b = vec_b.reshape(1, -1)
    return cosine_similarity(vec_a, vec_b)[0][0]


def perceptual_image_hash(image_path):
    try:
        phash = imagehash.phash(Image.open(image_path))
        return str(phash)
    except Exception as e:
        print(f"[ERROR] Не удалось получить хэш изображения: {e}")
        return None


def compare_hashes(hash1, hash2):
    return bin(int(hash1, 16) ^ int(hash2, 16)).count("1")