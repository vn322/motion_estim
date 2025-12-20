# main.py
import sys
import cv2
import os
import time
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget,
    QLabel, QHBoxLayout, QFileDialog, QMessageBox
)
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QImage, QPixmap
from pose_analyzer import PoseAnalyzer
from report_generator import save_video_with_overlay, save_csv_report

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Анализ движений")
        self.setGeometry(100, 100, 800, 600)
        self.analyzer = None
        self.cap = None
        self.frames = []
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)

        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout()

        self.video_label = QLabel()
        self.video_label.setAlignment(Qt.AlignCenter)
        self.video_label.setStyleSheet("background: #222; color: white;")
        self.video_label.setMinimumHeight(400)
        layout.addWidget(self.video_label)

        btns = QHBoxLayout()
        self._add_btn("📹 Камера", self.use_camera, "#4CAF50", btns)
        self._add_btn("📁 Видео", self.load_video, "#2196F3", btns)
        self._add_btn("🔄 Зеркало", self.toggle_flip, "#FF9800", btns, "flip")
        self._add_btn("🔁 180°", self.toggle_rotate, "#9C27B0", btns, "rot")
        self._add_btn("✅ Завершить", self.finish, "#4CAF50", btns, "finish")
        layout.addLayout(btns)

        central.setLayout(layout)

    def _add_btn(self, text, slot, color, layout, name=""):
        btn = QPushButton(text)
        btn.setStyleSheet(f"font-size: 24px; padding: 15px; background: {color}; color: white; border-radius: 10px;")
        btn.clicked.connect(slot)
        if name == "flip":
            self.btn_flip = btn
            btn.setVisible(False)
        elif name == "rot":
            self.btn_rot = btn
            btn.setVisible(False)
        elif name == "finish":
            self.btn_finish = btn
            btn.setVisible(False)
        layout.addWidget(btn)

    def use_camera(self):
        self.start(0)
        self._show_controls(True)

    def load_video(self):
        path, _ = QFileDialog.getOpenFileName(self, "Видео", "", "Video (*.mp4 *.avi)")
        if path:
            self.start(path)
            self._show_controls(False)

    def _show_controls(self, show):
        self.btn_flip.setVisible(show)
        self.btn_rot.setVisible(show)
        self.btn_finish.setVisible(show)

    def start(self, src):
        if self.cap: self.cap.release()
        self.cap = cv2.VideoCapture(src)
        if not self.cap.isOpened():
            QMessageBox.critical(self, "Ошибка", "Не удалось открыть источник.")
            return
        self.analyzer = PoseAnalyzer()
        self.frames = []
        self.timer.start(33)

    def toggle_flip(self):
        if self.analyzer: self.analyzer.flip_camera = not self.analyzer.flip_camera

    def toggle_rotate(self):
        if self.analyzer: self.analyzer.rotate_180 = not self.analyzer.rotate_180

    def update_frame(self):
        ret, frame = self.cap.read()
        if not ret:
            self.finish()
            return
        if self.analyzer:
            annot, _ = self.analyzer.process_frame(frame)
            self.frames.append(annot)
            h, w, ch = annot.shape
            qimg = QImage(annot.data, w, h, ch * w, QImage.Format_BGR888)
            self.video_label.setPixmap(QPixmap.fromImage(qimg).scaled(
                self.video_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation
            ))

    def finish(self):
        self.timer.stop()
        if self.cap: self.cap.release()
        os.makedirs("output", exist_ok=True)
        t = int(time.time())
        save_video_with_overlay(f"output/video_{t}.mp4", self.frames)
        save_csv_report(f"output/data_{t}.csv", self.analyzer.frame_data_log)
        QMessageBox.information(self, "✅ Готово", "Видео и CSV сохранены в папку 'output'.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())