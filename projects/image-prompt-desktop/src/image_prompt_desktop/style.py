APP_STYLE = """
QMainWindow {
  background: #f5efe7;
}

QWidget {
  color: #2f241d;
  font-family: "Yu Gothic UI", "Meiryo", sans-serif;
  font-size: 13px;
}

QLabel#TitleLabel {
  font-size: 22px;
  font-weight: 800;
  color: #241a15;
}

QLabel#SectionLabel {
  font-size: 14px;
  font-weight: 800;
  color: #4d3529;
}

QLabel#MetaLabel {
  color: #765e52;
}

QLabel#EmptyStateLabel {
  color: #765e52;
  background: #f7efe6;
  border: 1px dashed rgba(83, 55, 39, 0.18);
  border-radius: 12px;
  padding: 10px 12px;
}

QFrame#Panel {
  background: #fffaf3;
  border: 1px solid rgba(83, 55, 39, 0.14);
  border-radius: 16px;
}

QListWidget {
  background: #fffdf8;
  border: 1px solid rgba(83, 55, 39, 0.16);
  border-radius: 12px;
  padding: 6px;
}

QListWidget::item {
  min-height: 30px;
  padding: 7px 9px;
  border-radius: 8px;
}

QListWidget::item:selected {
  background: #d9672f;
  color: white;
}

QListWidget::item:hover {
  background: #f1dfd1;
}

QTabWidget::pane {
  border: 0;
}

QTabBar::tab {
  background: #ead8c5;
  border: 1px solid rgba(83, 55, 39, 0.14);
  border-bottom: 0;
  border-top-left-radius: 10px;
  border-top-right-radius: 10px;
  padding: 8px 12px;
  margin-right: 4px;
  font-weight: 700;
}

QTabBar::tab:selected {
  background: #fffaf3;
  color: #9f431f;
}

QPlainTextEdit,
QLineEdit {
  background: #fffdf8;
  border: 1px solid rgba(83, 55, 39, 0.22);
  border-radius: 12px;
  padding: 10px;
  selection-background-color: #f0a36a;
}

QPlainTextEdit:focus,
QLineEdit:focus {
  border: 2px solid #d9672f;
}

QPushButton {
  background: #efe1d2;
  border: 1px solid rgba(83, 55, 39, 0.14);
  border-radius: 12px;
  padding: 8px 12px;
  font-weight: 700;
}

QPushButton:hover {
  background: #e9d4c0;
}

QPushButton#PrimaryButton {
  background: #d9672f;
  color: white;
}

QPushButton#PrimaryButton:hover {
  background: #c85724;
}

QStatusBar {
  background: #fffaf3;
  color: #5f493e;
}
"""
