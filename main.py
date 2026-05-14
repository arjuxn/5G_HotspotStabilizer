import sys
import time
import threading
import psutil
import pydivert

from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QLabel,
    QPushButton,
    QVBoxLayout
)

MAX_MBPS = 8
DELAY = 0.004
WINDOW_DURATION = 0.05

running = False


def run_limiter(speed_label, status_label):
    global running

    MAX_BYTES_PER_SEC = (
        MAX_MBPS * 1_000_000
    ) / 8

    MAX_BYTES_PER_WINDOW = (
        MAX_BYTES_PER_SEC
        * WINDOW_DURATION
    )

    bytes_in_window = 0
    window_start = time.time()

    old_data = psutil.net_io_counters()
    speed_timer = time.time()

    with pydivert.WinDivert("true") as w:

        while running:

            packet = w.recv()

            current_time = time.time()
            packet_size = len(packet.raw)

            # Update speed display
            if current_time - speed_timer >= 1:

                new_data = psutil.net_io_counters()

                bytes_recv = (
                    new_data.bytes_recv
                    - old_data.bytes_recv
                )

                mb_per_sec = (
                    bytes_recv
                ) / 1_000_000

                mbps = (
                    bytes_recv * 8
                ) / 1_000_000

                speed_label.setText(
                    f"{mb_per_sec:.2f} MB/s  |  "
                    f"{mbps:.2f} Mbps"
                )

                old_data = new_data
                speed_timer = current_time

            # Pass outbound packets directly
            if not packet.is_inbound:
                w.send(packet)
                continue

            # Reset bandwidth window
            if (
                current_time
                - window_start
                >= WINDOW_DURATION
            ):

                bytes_in_window = 0
                window_start = current_time

            # Apply bandwidth shaping
            if (
                bytes_in_window
                + packet_size
                > MAX_BYTES_PER_WINDOW
            ):

                time.sleep(DELAY)

                bytes_in_window = 0
                window_start = time.time()

            w.send(packet)

            bytes_in_window += packet_size

    speed_label.setText(
        "0.00 MB/s  |  0.00 Mbps"
    )

    status_label.setText("Stopped")


class Window(QWidget):

    def __init__(self):

        super().__init__()

        self.setWindowTitle(
            "Jio 5G Stabilizer"
        )

        self.resize(500, 250)
        self.setMinimumSize(400, 200)

        self.setStyleSheet("""
            QWidget {
                background-color: #202124;
                color: white;
                font-family: Segoe UI;
            }

            QPushButton {
                background-color: #3c4043;
                border: none;
                padding: 10px;
                font-size: 15px;
                border-radius: 8px;
            }

            QPushButton:hover {
                background-color: #4a4d50;
            }
        """)

        self.speed_label = QLabel(
            "0.00 MB/s  |  0.00 Mbps"
        )

        self.speed_label.setStyleSheet(
            """
            font-size: 28px;
            font-weight: bold;
            padding: 10px;
            """
        )

        self.status_label = QLabel(
            "Stopped"
        )

        self.status_label.setStyleSheet(
            """
            font-size: 16px;
            color: red;
            padding-left: 10px;
            """
        )

        self.start_button = QPushButton(
            "Start"
        )

        self.stop_button = QPushButton(
            "Stop"
        )

        self.start_button.setMinimumHeight(45)
        self.stop_button.setMinimumHeight(45)

        self.start_button.clicked.connect(
            self.start_limiter
        )

        self.stop_button.clicked.connect(
            self.stop_limiter
        )

        layout = QVBoxLayout()

        layout.setSpacing(15)

        layout.setContentsMargins(
            20,
            20,
            20,
            20
        )

        layout.addWidget(self.speed_label)
        layout.addWidget(self.status_label)
        layout.addWidget(self.start_button)
        layout.addWidget(self.stop_button)

        self.setLayout(layout)

    def start_limiter(self):

        global running

        if running:
            return

        running = True

        self.status_label.setText(
            "Running"
        )

        self.status_label.setStyleSheet(
            """
            font-size: 16px;
            color: lightgreen;
            padding-left: 10px;
            """
        )

        threading.Thread(
            target=run_limiter,
            args=(
                self.speed_label,
                self.status_label
            ),
            daemon=True
        ).start()

    def stop_limiter(self):

        global running

        running = False

        self.speed_label.setText(
            "0.00 MB/s  |  0.00 Mbps"
        )

        self.status_label.setText(
            "Stopped"
        )

        self.status_label.setStyleSheet(
            """
            font-size: 16px;
            color: red;
            padding-left: 10px;
            """
        )


app = QApplication(sys.argv)

window = Window()

window.show()

sys.exit(app.exec())
