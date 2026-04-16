import cv2
import numpy as np
import onnxruntime as ort
import traceback
from core.yolo_decoder import YOLODecoder

try:
    img = np.zeros((800, 600, 3), dtype=np.uint8)
    decoder = YOLODecoder(imgsz=640)
    blob, r, pad, padded_shape = decoder.preprocess(img)
    print("blob shape:", blob.shape)

    session = ort.InferenceSession(r"E:\自作アプリ集\モザイクかけ太郎\ntd11_anime_nsfw_segm_v5-variant1.onnx", providers=['CPUExecutionProvider'])
    input_name = session.get_inputs()[0].name
    print("expected shape:", session.get_inputs()[0].shape)

    outputs = session.run(None, {input_name: blob})
    print("Run success!")
except Exception as e:
    traceback.print_exc()
