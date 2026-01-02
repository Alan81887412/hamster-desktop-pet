import sys
import os
import random
from PySide6.QtWidgets import QApplication, QLabel
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QPixmap, QTransform

# =====================
# 打包後也能找到資源的路徑工具（PyInstaller 必備）
# =====================
def resource_path(relative_path: str) -> str:
    # PyInstaller on macOS/Windows: resources extracted to _MEIPASS
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative_path)
    # running from source
    return os.path.join(os.path.abspath("."), relative_path)

# =====================
# 可調參數
# =====================
PET_SIZE = 75          # 桌寵顯示大小
MOVE_INTERVAL = 25      # 移動更新 (ms)
ANIM_INTERVAL = 75     # 動畫速度 (ms)
GRAVITY = 3.0
MAX_FALL_SPEED = 60


class DesktopPet(QLabel):
    def __init__(self):
        super().__init__()

        # ---------- 視窗屬性 ----------
        self.setWindowFlags(
            Qt.FramelessWindowHint |
            Qt.WindowStaysOnTopHint |
            Qt.Tool
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setScaledContents(True)

        # ---------- 載入動畫幀 ----------
        self.frames_right = []
        for i in range(1, 13):
            pix = QPixmap(resource_path(f"assets/hamster_trimmed/{i:02d}.png"))
            if not pix.isNull():
                self.frames_right.append(pix)

        if not self.frames_right:
            raise RuntimeError("沒有載入任何 hamster 圖片，請檢查 assets/hamster_trimmed")

        self.frames_left = [
            pix.transformed(QTransform().scale(-1, 1))
            for pix in self.frames_right
        ]

        self.frame_count = len(self.frames_right)
        self.frame_index = 0

        self.setPixmap(self.frames_right[0])
        self.resize(PET_SIZE, PET_SIZE)

        # ---------- 螢幕資訊 ----------
        screen = QApplication.primaryScreen()
        geo = screen.availableGeometry()

        self.x = random.randint(0, geo.width() - PET_SIZE)
        self.ground_y = geo.bottom() - PET_SIZE
        self.y = self.ground_y
        self.move(self.x, self.y)

        # ---------- 行為狀態 ----------
        self.direction = random.choice([-1, 1])
        self.speed = random.uniform(1.2, 3.5)

        self.dragging = False
        self.falling = False
        self.paused = False
        self.pause_time = 0
        self.fall_speed = 0

        # ---------- 移動 Timer ----------
        self.move_timer = QTimer(self)
        self.move_timer.timeout.connect(self.update_pet)
        self.move_timer.start(MOVE_INTERVAL)

        # ---------- 動畫 Timer ----------
        self.anim_timer = QTimer(self)
        self.anim_timer.timeout.connect(self.update_animation)
        self.anim_timer.start(ANIM_INTERVAL)

        self.show()
        self.raise_()

    # =====================
    # 動畫更新
    # =====================
    def update_animation(self):
        if self.dragging or self.falling or self.paused:
            return

        self.frame_index = (self.frame_index + 1) % self.frame_count

        if self.direction == 1:
            self.setPixmap(self.frames_right[self.frame_index])
        else:
            self.setPixmap(self.frames_left[self.frame_index])

    # =====================
    # 滑鼠事件
    # =====================
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragging = True
            self.falling = False
            self.paused = False
            self.fall_speed = 0
            self.drag_offset = event.globalPosition().toPoint() - self.pos()

    def mouseMoveEvent(self, event):
        if self.dragging:
            pos = event.globalPosition().toPoint() - self.drag_offset
            self.x = pos.x()
            self.y = pos.y()
            self.move(int(self.x), int(self.y))

    def mouseReleaseEvent(self, event):
        self.dragging = False
        self.falling = True
        self.fall_speed = 0

    # =====================
    # 行為邏輯
    # =====================
    def update_pet(self):
        if self.dragging:
            return

        if self.falling:
            self.fall_speed = min(self.fall_speed + GRAVITY, MAX_FALL_SPEED)
            self.y += self.fall_speed

            if self.y >= self.ground_y:
                self.y = self.ground_y
                self.falling = False
                self.paused = True
                self.pause_time = random.randint(60, 180)

            self.move(int(self.x), int(self.y))
            return

        if self.paused:
            self.pause_time -= 1
            if self.pause_time <= 0:
                self.paused = False
                self.speed = random.uniform(1.2, 3.5)
                self.direction = random.choice([-1, 1])
            return

        screen = QApplication.primaryScreen().availableGeometry()
        self.x += self.direction * self.speed

        if self.x <= 0:
            self.x = 0
            self.direction = 1
        elif self.x + PET_SIZE >= screen.width():
            self.x = screen.width() - PET_SIZE
            self.direction = -1

        self.y = self.ground_y
        self.move(int(self.x), int(self.y))


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # 必須保留強參考，否則視窗可能瞬間消失
    pets = []
    pets.append(DesktopPet())

    sys.exit(app.exec())
