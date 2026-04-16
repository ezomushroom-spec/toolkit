import cv2
import numpy as np
import logging

logger = logging.getLogger(__name__)

class ImageFilterUtils:
    @staticmethod
    def create_filtered_full_image(img: np.ndarray, mask_type: str, strength: float) -> np.ndarray:
        """
        画像全体に対して指定されたフィルタ（モザイク、ぼかし等）を適用した画像を生成する。
        """
        h, w = img.shape[:2]
        filtered = img.copy()
        try:
            val = int(strength)
            if mask_type == "pixel":
                px = max(1, val)
                small = cv2.resize(img, (max(1, w // px), max(1, h // px)), interpolation=cv2.INTER_NEAREST)
                filtered = cv2.resize(small, (w, h), interpolation=cv2.INTER_NEAREST)
            elif mask_type == "blur":
                k = val
                if k % 2 == 0: 
                    k += 1
                filtered = cv2.GaussianBlur(img, (k, k), 0)
            elif mask_type == "black":
                filtered[:] = (0, 0, 0)
            elif mask_type == "white":
                filtered[:] = (255, 255, 255)
        except Exception as e:
            logger.error(f"Failed to create full filtered image. Error: {e}")
        return filtered

    @staticmethod
    def apply_filter_box(img: np.ndarray, candidates: list, mask_type: str, strength: float, margin: float) -> np.ndarray:
        """
        指定された矩形（Box）領域にフィルタを適用する。
        """
        h_img, w_img = img.shape[:2]
        processed_img = img.copy()
        margin_int = int(margin)
        strength_int = int(strength)

        for item in candidates:
            # item['xyxy'] は [x1, y1, x2, y2]
            x1, y1, x2, y2 = map(int, item['xyxy'])
            
            x1 = max(0, x1 - margin_int)
            y1 = max(0, y1 - margin_int)
            x2 = min(w_img, x2 + margin_int)
            y2 = min(h_img, y2 + margin_int)
            
            w, h = x2 - x1, y2 - y1
            if w <= 0 or h <= 0: 
                continue

            roi = processed_img[y1:y2, x1:x2]
            try:
                if mask_type == "pixel":
                    px = max(1, strength_int)
                    small = cv2.resize(roi, (max(1, w // px), max(1, h // px)), interpolation=cv2.INTER_NEAREST)
                    processed_img[y1:y2, x1:x2] = cv2.resize(small, (w, h), interpolation=cv2.INTER_NEAREST)
                elif mask_type == "blur":
                    k = strength_int
                    if k % 2 == 0: 
                        k += 1
                    processed_img[y1:y2, x1:x2] = cv2.GaussianBlur(roi, (k, k), 0)
                elif mask_type == "black":
                    processed_img[y1:y2, x1:x2] = (0, 0, 0)
                elif mask_type == "white":
                    processed_img[y1:y2, x1:x2] = (255, 255, 255)
            except Exception as e:
                logger.error(f"Failed to apply filter to box region. Error: {e}")
        return processed_img

    @staticmethod
    def apply_filter_mask(img: np.ndarray, candidates: list, mask_type: str, strength: float, margin: float) -> np.ndarray:
        """
        指定されたセグメンテーション（Mask）領域に沿ってフィルタを適用する。
        """
        h_img, w_img = img.shape[:2]
        if not candidates: 
            return img.copy()

        try:
            combined_mask = np.zeros((h_img, w_img), dtype=np.uint8)
            margin_int = int(margin)

            for item in candidates:
                mask_np = item.get('mask')
                if mask_np is None: 
                    continue

                if mask_np.max() <= 1.0: 
                    mask_np = (mask_np * 255).astype('uint8')
                
                mask_resized = cv2.resize(mask_np, (w_img, h_img), interpolation=cv2.INTER_LINEAR)
                _, mask_binary = cv2.threshold(mask_resized, 127, 255, cv2.THRESH_BINARY)
                
                if margin_int > 0:
                    k_size = margin_int * 2 + 1
                    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (k_size, k_size))
                    mask_binary = cv2.dilate(mask_binary, kernel, iterations=1)

                combined_mask = cv2.bitwise_or(combined_mask, mask_binary)
                
            if cv2.countNonZero(combined_mask) == 0: 
                return img.copy()

            # マスク用の完全なフィルタ適用画像を用意する
            filtered_full = ImageFilterUtils.create_filtered_full_image(img, mask_type, strength)
            mask_3ch = cv2.merge([combined_mask, combined_mask, combined_mask])
            
            # マスク部分だけフィルタ画像に差し替える
            final_img = np.where(mask_3ch == 255, filtered_full, img)
            return final_img.astype(np.uint8)
        except Exception as e:
            logger.error(f"Failed to apply filter mask. Error: {e}")
            return img.copy()
