from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QSizePolicy,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


class WorkCardWidget(QFrame):
    open_requested = Signal(int)
    review_requested = Signal(int)
    delete_requested = Signal(int)

    def __init__(self, summary: dict[str, object], parent: QWidget | None = None) -> None:
        super().__init__(parent)
        work = summary["work"]
        self.work_id = int(work["id"])
        self.work_name = str(work["name"])
        self.setObjectName("workCard")
        self.setFrameShape(QFrame.Shape.StyledPanel)

        root = QHBoxLayout(self)
        root.setContentsMargins(16, 16, 16, 16)
        root.setSpacing(16)

        thumbnail = QLabel("No Image")
        thumbnail.setFixedSize(96, 96)
        thumbnail.setObjectName("thumbnailBox")
        thumbnail.setAlignment(Qt.AlignmentFlag.AlignCenter)
        thumbnail_path = summary.get("thumbnail_path")
        if isinstance(thumbnail_path, str) and Path(thumbnail_path).exists():
            pixmap = QPixmap(thumbnail_path)
            if not pixmap.isNull():
                thumbnail.setPixmap(
                    pixmap.scaled(
                        96,
                        96,
                        Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                        Qt.TransformationMode.SmoothTransformation,
                    )
                )
        root.addWidget(thumbnail)

        info_layout = QVBoxLayout()
        info_layout.setSpacing(6)
        name_label = QLabel(self.work_name)
        name_label.setStyleSheet("font-size: 16px; font-weight: 700;")
        name_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        status_label = QLabel(str(work["status"]))
        status_label.setProperty("statusChip", str(work["status"]))
        count_label = QLabel(f"画像: {summary['image_count']}枚")
        updated_label = QLabel(f"更新: {work['updated_at']}")
        memo_label = QLabel("メモあり" if str(work["memo"]).strip() else "メモなし")
        info_layout.addWidget(name_label)
        meta_row = QHBoxLayout()
        meta_row.addWidget(status_label)
        meta_row.addWidget(count_label)
        meta_row.addStretch()
        info_layout.addLayout(meta_row)
        info_layout.addWidget(updated_label)
        info_layout.addWidget(memo_label)
        destination_row = QHBoxLayout()
        destination_row.setSpacing(6)
        for destination in list(summary["destination_summary"])[:3]:
            chip = QLabel(f"{destination['name']}: {destination['status']}")
            chip.setProperty("destinationChip", str(destination["status"]))
            destination_row.addWidget(chip)
        destination_row.addStretch()
        info_layout.addLayout(destination_row)
        root.addLayout(info_layout, stretch=1)

        actions_layout = QVBoxLayout()
        open_button = QPushButton("開く")
        review_button = QPushButton("確認")
        delete_button = QPushButton("削除")
        open_button.setProperty("role", "primary")
        delete_button.setProperty("role", "danger")
        actions_layout.addWidget(open_button)
        actions_layout.addWidget(review_button)
        actions_layout.addWidget(delete_button)
        actions_layout.addStretch()
        root.addLayout(actions_layout)

        open_button.clicked.connect(lambda: self.open_requested.emit(self.work_id))
        review_button.clicked.connect(lambda: self.review_requested.emit(self.work_id))
        delete_button.clicked.connect(lambda: self.delete_requested.emit(self.work_id))
