import nixio as nix
import numpy as np
import matplotlib.pyplot as plt
from IPython import embed

def line(p1, p2):
    a = (p1[1] - p2[1])
    b = (p2[0] - p1[0])
    c = (p1[0]*p2[1] - p2[0]*p1[1])
    return a, b, -c


def intersection(l1, l2):
    d = l1[0] * l2[1] - l1[1] * l2[0]
    dx = l1[2] * l2[1] - l1[1] * l2[2]
    dy = l1[0] * l2[2] - l1[2] * l2[0]
    if d != 0:
        x = dx / d
        y = dy / d
        return x, y
    else:
        return False


def threshold_crossings(data, time, threshold=0.0):
    # threshold = np.max(data) - (np.max(data) - np.min(data))/2
    indices = np.where((data > threshold) & (np.roll(data, 1) <= threshold))[0]
    times = time[indices]
    return times, indices


def detect_eod_times(time, eod, threshold):
    _, idx = threshold_crossings(eod, time, threshold)
    thresh = line([time[0], threshold], [time[-1], threshold])
    times = np.zeros(idx.shape)
    for j, i in enumerate(idx):
        if i >= len(time) - 1:
            continue
        else:
            l1 = line([time[i - 1], eod[i - 1]], [time[i + 1], eod[i + 1]])
            pos = intersection(l1, thresh)
        if pos is False:
            continue
        else:
            times[j] = pos[0]

    return times, idx

if __name__ == "__main__":
    f = nix.File.open("../data/2020-12-15-ag-apteronotus/2020-12-15-ag-apteronotus.nix")
    b = f.blocks[0]
    eod = b.data_arrays["EOD"][:1000]
    eod -=np.mean(eod)
    time = np.arange(0, len(eod)) * 1/20000
    times, _ = detect_eod_times(time, eod)
    plt.plot(time, eod, marker=".", markersize=4)
    plt.scatter(times, np.zeros_like(times), color="tab:red")
    plt.show()

