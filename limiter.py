import pydivert
import psutil
import threading
import time

# SETTINGS

MAX_MBPS = 8

DELAY = 0.004

WINDOW_DURATION = 0.05

# CALCULATIONS

MAX_BYTES_PER_SEC = (
    MAX_MBPS * 1_000_000
) / 8

MAX_BYTES_PER_WINDOW = (
    MAX_BYTES_PER_SEC * WINDOW_DURATION
)


# SPEED MONITOR

def monitor_speed():

    old_data = psutil.net_io_counters()

    while True:

        time.sleep(1)

        new_data = psutil.net_io_counters()

        bytes_recv = (
            new_data.bytes_recv
            - old_data.bytes_recv
        )

        
        mbps = (
            bytes_recv * 8
        ) / 1_000_000

        
        mb_per_sec = (
            bytes_recv
        ) / 1_000_000

        print(
            f"Download Speed: "
            f"{mbps:.2f} Mbps "
            f"({mb_per_sec:.2f} MB/s)"
        )

        old_data = new_data


# START MONITOR THREAD


threading.Thread(
    target=monitor_speed,
    daemon=True
).start()


# VARIABLES


bytes_in_window = 0
window_start = time.time()

print("\n==============================")
print(" Jio 5G Stabilizer Running ")
print("==============================")
print(f"Target Speed : {MAX_MBPS} Mbps")
print(f"Delay        : {DELAY} sec")
print(f"Window        : {WINDOW_DURATION} sec\n")

#MAIN

with pydivert.WinDivert("true") as w:

    for packet in w:

        current_time = time.time()

        packet_size = len(packet.raw)

        if not packet.is_inbound:
            w.send(packet)
            continue

        if (
            current_time - window_start
            >= WINDOW_DURATION
        ):

            bytes_in_window = 0
            window_start = current_time


        if (
            bytes_in_window + packet_size
            > MAX_BYTES_PER_WINDOW
        ):

            time.sleep(DELAY)

            bytes_in_window = 0
            window_start = time.time()


        w.send(packet)

        bytes_in_window += packet_size
