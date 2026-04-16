import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer
from PIL import Image
from ui.preview_panel import InteractivePreview, pil_to_qpixmap

def main():
    app = QApplication(sys.argv)
    preview = InteractivePreview()
    preview.show()
    preview.resize(800, 600)
    
    img = Image.new('RGB', (1200, 900), color='green')
    pix = pil_to_qpixmap(img)
    
    preview.set_cell_bounds({0: (0, 0, 600, 900), 1: (600, 0, 600, 900)}, (1200, 900))
    preview.set_source_images({0: img, 1: img})
    preview.set_source_pixmap(pix)
    
    def capture():
        preview.grab().save('test_gui_render.png')
        QApplication.quit()
        
    QTimer.singleShot(1000, capture)
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
