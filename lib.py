import os
import time


def simple_hash(s, range_size):
    # Compute the sum of ASCII values of the characters in the string
    ascii_sum = sum(ord(c) for c in s)
    # Take the modulo of the sum with the size of the range
    return ascii_sum % range_size


def logger(filename, message):
    if os.path.exists(filename):
        logFile = open(filename, "a")
        logFile.write(message)
        logFile.close()

    else:
        with open(filename, "w") as logFile:
            logFile.write("Server Log")
            logFile.write(message)


def berkeley(nodeClocks):
    differences = []
    masterClock = nodeClocks[-1]
    for clock in nodeClocks:
        differences.append(clock - masterClock)
    totalTimeDifference = sum(differences)
    averageTimeDifference = totalTimeDifference / len(nodeClocks)
    synchronizedTime = masterClock + averageTimeDifference
    return synchronizedTime


def compute_formatted_time(offset):
    currentTime = offset + time.time()
    timeStruct = time.localtime(currentTime)
    formattedTime = time.strftime("%Y-%m-%d %H:%M:%S", timeStruct)
    preciseTime = f"{formattedTime}.0"
    return preciseTime
