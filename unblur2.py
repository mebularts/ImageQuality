import cv2
import numpy as np
from PyQt5.QtWidgets import QApplication, QGraphicsView, QGraphicsScene, QLabel, QMainWindow, QVBoxLayout, QSlider, QPushButton, QWidget, QFileDialog
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import Qt, pyqtSignal

class ImageDropArea(QLabel):
    imageDropped = pyqtSignal(str)

    def __init__(self, parent):
        super().__init__(parent)
        self.setAlignment(Qt.AlignCenter)
        self.setAcceptDrops(True)

    def dragEnterEvent(self, event):
        mime_data = event.mimeData()
        if mime_data.hasUrls() and mime_data.urls()[0].isLocalFile():
            event.acceptProposedAction()

    def dropEvent(self, event):
        mime_data = event.mimeData()
        if mime_data.hasUrls() and mime_data.urls()[0].isLocalFile():
            file_path = mime_data.urls()[0].toLocalFile()
            self.imageDropped.emit(file_path)

class ImageEnhancer(QMainWindow):
    def __init__(self):
        super().__init__()

        self.image_path = None
        self.scale_factor = 2
        self.sharpening_factor = 1
        self.original_image = None
        self.enhanced_image = None

        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Image Enhancer")
        self.setGeometry(100, 100, 800, 600)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.drop_area = ImageDropArea(self)
        self.drop_area.imageDropped.connect(self.load_image)

        self.graphics_view = QGraphicsView(self)
        self.graphics_scene = QGraphicsScene(self)
        self.graphics_view.setScene(self.graphics_scene)

        self.scale_slider = QSlider(Qt.Horizontal)
        self.scale_slider.setMinimum(2)
        self.scale_slider.setMaximum(16)
        self.scale_slider.setValue(self.scale_factor)
        self.scale_slider.valueChanged.connect(self.update_scale_factor)

        self.sharpening_slider = QSlider(Qt.Horizontal)
        self.sharpening_slider.setMinimum(0)
        self.sharpening_slider.setMaximum(10)
        self.sharpening_slider.setValue(self.sharpening_factor)
        self.sharpening_slider.valueChanged.connect(self.update_sharpening_factor)

        self.load_button = QPushButton("Load Image", self)
        self.load_button.clicked.connect(self.load_from_dialog)

        self.preview_button = QPushButton("Preview", self)
        self.preview_button.clicked.connect(self.preview)

        self.save_button = QPushButton("Save Image", self)
        self.save_button.clicked.connect(self.save_image)
        self.save_button.setEnabled(False)

        layout = QVBoxLayout()
        layout.addWidget(self.drop_area)
        layout.addWidget(self.graphics_view)
        layout.addWidget(self.scale_slider)
        layout.addWidget(self.sharpening_slider)
        layout.addWidget(self.load_button)
        layout.addWidget(self.preview_button)
        layout.addWidget(self.save_button)

        self.central_widget.setLayout(layout)

    def load_from_dialog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        file_name, _ = QFileDialog.getOpenFileName(self, "Open Image", "", "Images (*.png *.jpg *.webp);;All Files (*)", options=options)
        if file_name:
            self.load_image(file_name)

    def load_image(self, file_path):
        self.image_path = file_path
        self.original_image = cv2.imread(self.image_path)
        self.display_image(self.original_image)

    def display_image(self, image):
        height, width, channel = image.shape
        bytes_per_line = 3 * width
        q_image = QImage(image.data, width, height, bytes_per_line, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(q_image)
        self.graphics_scene.clear()
        self.graphics_scene.addPixmap(pixmap)

    def update_scale_factor(self, value):
        self.scale_factor = value

    def update_sharpening_factor(self, value):
        self.sharpening_factor = value / 10.0  # Scale to a reasonable range (0.0 to 1.0)

    def preview(self):
        if self.image_path:
            self.enhanced_image = self.enhance_image(self.original_image, self.scale_factor, self.sharpening_factor)
            self.display_image(self.enhanced_image)
            self.save_button.setEnabled(True)

    def enhance_image(self, image, scale_factor, sharpening_factor):
        h, w, _ = image.shape
        new_size = (int(w * scale_factor), int(h * scale_factor))
        sr_image = cv2.resize(image, new_size, interpolation=cv2.INTER_CUBIC)

        # Apply Unsharp Mask for sharpening
        blurred = cv2.GaussianBlur(sr_image, (0, 0), scale_factor)
        sharpened = cv2.addWeighted(sr_image, 1.0 + sharpening_factor, blurred, -sharpening_factor, 0)

        return sharpened

    def save_image(self):
        save_path, _ = QFileDialog.getSaveFileName(self, "Save Image", "", "Images (*.png *.jpg *.webp);;All Files (*)")
        if save_path:
            cv2.imwrite(save_path, self.enhanced_image)

if __name__ == '__main__':
    app = QApplication([])
    window = ImageEnhancer()
    window.show()
    app.exec_()
