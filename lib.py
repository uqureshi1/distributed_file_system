import os
import time
from typing import List, Any


def simple_hash(s: str, range_size: int) -> int:
    # Compute the sum of ASCII values of the characters in the string
    ascii_sum = sum(ord(c) for c in s)
    # Take the modulo of the sum with the size of the range
    return ascii_sum % range_size


def logger(filename: str, message: str) -> None:
    if os.path.exists(filename):
        log_file = open(filename, "a")
        log_file.write(message)
        log_file.close()

    else:
        with open(filename, "w") as log_file:
            log_file.write("Server Log")
            log_file.write(message)


def berkeley(node_clocks: List) -> Any:
    differences = []
    master_clock = node_clocks[-1]
    for clock in node_clocks:
        differences.append(clock - master_clock)
    total_time_difference = sum(differences)
    average_time_difference = total_time_difference / len(node_clocks)
    synchronized_time = master_clock + average_time_difference
    return synchronized_time


def compute_formatted_time(offset: int) -> str:
    current_time = offset + time.time()
    time_struct = time.localtime(current_time)
    formatted_time = time.strftime("%Y-%m-%d %H:%M:%S", time_struct)
    precise_time = f"{formatted_time}.0"
    return precise_time
