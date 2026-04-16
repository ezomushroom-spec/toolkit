import cv2
import numpy as np

class YOLODecoder:
    """
    ONNX化されたYOLOv8/11セグメンテーションモデルの出力をパースし、
    バウンディングボックスとマスクを元の入力画像サイズに合わせて復元するクラス
    """
    def __init__(self, imgsz=1024, conf_thres=0.25, iou_thres=0.45):
        self.imgsz = imgsz
        self.conf_thres = conf_thres
        self.iou_thres = iou_thres

    def preprocess(self, img):
        # Letterbox resize (アスペクト比を維持してパディング)
        shape = img.shape[:2]  # [height, width]
        
        r = min(self.imgsz / shape[0], self.imgsz / shape[1])
        new_unpad = int(round(shape[1] * r)), int(round(shape[0] * r))
        
        dw, dh = self.imgsz - new_unpad[0], self.imgsz - new_unpad[1]
        dw, dh = dw / 2, dh / 2

        if shape[::-1] != new_unpad:
            img_res = cv2.resize(img, new_unpad, interpolation=cv2.INTER_LINEAR)
        else:
            img_res = img.copy()

        top, bottom = int(round(dh - 0.1)), int(round(dh + 0.1))
        left, right = int(round(dw - 0.1)), int(round(dw + 0.1))
        img_padded = cv2.copyMakeBorder(img_res, top, bottom, left, right, cv2.BORDER_CONSTANT, value=(114, 114, 114))

        # HWC -> CHW, BGR -> RGB変換と1/255での正規化
        blob = img_padded[..., ::-1].transpose((2, 0, 1))
        blob = np.ascontiguousarray(blob, dtype=np.float32) / 255.0
        blob = np.expand_dims(blob, axis=0) # [1, 3, H, W]
        
        return blob, r, (dw, dh), img_padded.shape[:2]

    def postprocess(self, outputs, r, pad, orig_shape, padded_shape, target_classes=None):
        """
        outputs[0]: (1, 4 + nc + nm, 分割グリッド数) -> バウンディングボックスとスコア、マスク係数
        outputs[1]: (1, nm, h, w) -> マスクプロトタイプ
        """
        if len(outputs) < 2:
            return []
            
        box_data = outputs[0][0]   # (4 + nc + nm, grids)
        proto_data = outputs[1][0] # (nm, h, w)

        box_data = box_data.T # (grids, 4 + nc + nm)
        
        nm = proto_data.shape[0]
        nc = box_data.shape[1] - 4 - nm
        if nc < 1: nc = 1
        
        boxes = box_data[:, :4]
        scores = box_data[:, 4:4+nc]
        mask_coeffs = box_data[:, 4+nc:]

        class_ids = np.argmax(scores, axis=1)
        confidences = np.max(scores, axis=1)

        # 閾値でフィルタリング
        mask = confidences > self.conf_thres
        
        # クラスIDでフィルタリング（指定クラス名と一致するものだけを検知）
        if target_classes is not None and len(target_classes) > 0:
            class_mask = np.isin(class_ids, target_classes)
            mask = mask & class_mask

        boxes = boxes[mask]
        confidences = confidences[mask]
        class_ids = class_ids[mask]
        mask_coeffs = mask_coeffs[mask]

        if len(boxes) == 0:
            return []

        # cx, cy, w, h を x1, y1, x2, y2 に変換
        x = boxes[:, 0]
        y = boxes[:, 1]
        w = boxes[:, 2]
        h = boxes[:, 3]
        boxes_xyxy = np.column_stack([x - w/2, y - h/2, x + w/2, y + h/2])

        # NMS（重複枠の排除）
        indices = cv2.dnn.NMSBoxes(boxes_xyxy.tolist(), confidences.tolist(), self.conf_thres, self.iou_thres)
        if len(indices) == 0:
            return []
        
        indices = indices.flatten()
        
        boxes_xyxy = boxes_xyxy[indices]
        confidences = confidences[indices]
        class_ids = class_ids[indices]
        mask_coeffs = mask_coeffs[indices]

        # マスク係数とプロトタイプを掛け合わせてSigmoid層を通しマスクを生成
        c, mh, mw = proto_data.shape
        masks = mask_coeffs @ proto_data.reshape(c, -1) # (N, mh * mw)
        masks = self.sigmoid(masks)
        masks = masks.reshape(-1, mh, mw) # (N, mh, mw)

        # ボックス座標を元の画像サイズにスケールバック
        boxes_xyxy[:, [0, 2]] -= pad[0]
        boxes_xyxy[:, [1, 3]] -= pad[1]
        boxes_xyxy /= r
        
        boxes_xyxy[:, [0, 2]] = np.clip(boxes_xyxy[:, [0, 2]], 0, orig_shape[1])
        boxes_xyxy[:, [1, 3]] = np.clip(boxes_xyxy[:, [1, 3]], 0, orig_shape[0])

        candidates = []
        for i in range(len(indices)):
            mask_img = masks[i]
            
            # マスクをパディング済みのサイズにリサイズ
            mask_img = cv2.resize(mask_img, (padded_shape[1], padded_shape[0]), interpolation=cv2.INTER_LINEAR)
            
            # パディング部分をクロップして元の比率に戻す
            top, bottom = int(round(pad[1] - 0.1)), int(round(pad[1] + 0.1))
            left, right = int(round(pad[0] - 0.1)), int(round(pad[0] + 0.1))
            
            mask_unpad = mask_img[top:padded_shape[0]-bottom, left:padded_shape[1]-right]

            # 元の入力画像の解像度にリサイズ
            if mask_unpad.shape[:2] != orig_shape:
                mask_final = cv2.resize(mask_unpad, (orig_shape[1], orig_shape[0]), interpolation=cv2.INTER_LINEAR)
            else:
                mask_final = mask_unpad
                
            # バウンディングボックス外のマスク領域をゼロにする（モザイク範囲のはみ出し・過剰検知を防ぐ）
            x1, y1, x2, y2 = map(int, map(round, boxes_xyxy[i]))
            x1, y1 = max(0, x1), max(0, y1)
            x2, y2 = min(orig_shape[1], x2), min(orig_shape[0], y2)
            
            mask_cropped = np.zeros_like(mask_final)
            if x2 > x1 and y2 > y1:
                mask_cropped[y1:y2, x1:x2] = mask_final[y1:y2, x1:x2]
                
            candidates.append({
                'cls_id': int(class_ids[i]),
                'conf': float(confidences[i]),
                'xyxy': boxes_xyxy[i].tolist(),
                'mask': mask_cropped 
            })

        return candidates

    def sigmoid(self, x):
        # オーバーフローを回避する安全なシグモイド
        return np.where(x >= 0, 
                        1 / (1 + np.exp(-x)), 
                        np.exp(x) / (1 + np.exp(x)))
