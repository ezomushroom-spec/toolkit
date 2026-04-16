import sys
from PySide6.QtWidgets import QApplication
from ui.main_window import MainWindow
from pathlib import Path

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    
    # We need a valid test image. Creating one:
    from PIL import Image
    test_img_path = Path("test_image_123.jpg")
    img = Image.new('RGB', (800, 600), color='red')
    img.save(test_img_path)
    
    # simulate drop
    window._on_images_dropped([test_img_path, test_img_path])
    
    # Select vsplit
    window._on_preset_changed("vsplit")
    
    # Wait for QRunnable thread to finish
    import time
    from PySide6.QtCore import QTimer
    def capture():
        print("Capturing end state...")
        window.preview_panel._preview_label.grab().save("test_main_window_render.png")
        QApplication.quit()
        
    QTimer.singleShot(1000, capture)
    app.exec()

if __name__ == "__main__":
    main()
