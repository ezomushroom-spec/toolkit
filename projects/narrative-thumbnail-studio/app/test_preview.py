import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QPixmap, QImage, QPainter
from PySide6.QtCore import QRectF
from ui.preview_panel import InteractivePreview, ClippedPixmapItem

def main():
    app = QApplication(sys.argv)
    preview = InteractivePreview()
    preview.show()
    preview.resize(800, 600)
    
    # Check scene size
    print("Output size:", preview._output_size)
    print("Viewport size:", preview.viewport().size())
    print("Scene rect:", preview.scene_obj.sceneRect())
    print("View transform pre-update:", preview.transform())
    
    from PIL import Image
    import numpy as np
    # Create dummy image
    img = Image.new('RGB', (1200, 900), color='green')
    from ui.preview_panel import pil_to_qpixmap
    pix = pil_to_qpixmap(img)
    preview.set_source_pixmap(pix)
    
    preview.set_cell_bounds({0: (0, 0, 600, 900), 1: (600, 0, 600, 900)}, (1200, 900))
    preview.set_source_images({0: img, 1: img})
    preview.set_hq_mode(True)
    
    # render
    img_grab = preview.grab()
    img_grab.save('test_render.png')

if __name__ == '__main__':
    main()
