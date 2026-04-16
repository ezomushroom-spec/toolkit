import os
import cv2
import numpy as np
import logging

logger = logging.getLogger(__name__)

def imread_safe(file_path: str, flags: int = cv2.IMREAD_COLOR) -> np.ndarray:
    """
    日本語を含むパスからでも安全に画像を読み込む
    cv2.imread の代替として使用
    """
    try:
        # np.fromfile はパスにマルチバイト文字が含まれていても読み込み可能
        img_array = np.fromfile(file_path, dtype=np.uint8)
        img = cv2.imdecode(img_array, flags)
        if img is None:
            logger.error(f"Failed to decode image: {file_path}")
        return img
    except Exception as e:
        logger.error(f"Error reading {file_path}: {e}")
        return None

def imwrite_safe(file_path: str, img: np.ndarray, params=None) -> bool:
    """
    日本語を含むパスへ安全に画像を書き込む
    cv2.imwrite の代替として使用
    """
    try:
        ext = os.path.splitext(file_path)[1].lower()
        if not ext:
            ext = '.jpg'
        
        encode_ext = ext if ext else '.jpg'
        if params is not None:
            result, buffer = cv2.imencode(encode_ext, img, params)
        else:
            result, buffer = cv2.imencode(encode_ext, img)
            
        if result:
            with open(file_path, mode='wb') as f:
                buffer.tofile(f)
            return True
        else:
            logger.error(f"Failed to encode image for {file_path}")
            return False
    except Exception as e:
        logger.error(f"Error writing {file_path}: {e}")
        return False
