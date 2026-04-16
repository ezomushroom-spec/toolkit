import sys
import os

try:
    from ultralytics import YOLO
except ImportError:
    print("エラー: ultralytics モジュールがインストールされていません。")
    print("変換を行う環境で 'pip install ultralytics' を実行してください。")
    sys.exit(1)

def export_model(pt_path):
    if not os.path.exists(pt_path):
        print(f"エラー: モデルファイルが見つかりません -> {pt_path}")
        sys.exit(1)
        
    print(f"ONNX形式への変換を開始します: {pt_path}")
    
    try:
        model = YOLO(pt_path)
        # NMSやスケーリングを内部に含まない標準のONNX出力を行う
        success = model.export(format="onnx", opset=15)
        print(f"\n変換が完了しました！出力ファイルは元ファイルと同じフォルダに保存されています。")
        print(f"結果: {success}")
    except Exception as e:
        print(f"変換中にエラーが発生しました: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("使い方: python export_onnx.py <モデルファイル.ptのパス>")
        sys.exit(1)
        
    export_model(sys.argv[1])
