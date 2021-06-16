from nix_helpers import read_eod
from helper_functions import cut_segments, calculate_amplitudes, read_eod_frequency
import matplotlib.pyplot as plt
from nix_helpers import read_jar_data
import numpy as np



segment_length = 0.05  # Segementlänge in sek
# time, eod = read_eod('../data/wave/2020-12-07-ag-barometrix/2020-12-07-ag-barometrix.nix', 30)
time, eod, df = read_jar_data('../data/JAR/2020-12-17-ai-majestix/2020-12-17-ai-majestix.nix', 50)

plt.plot(time, eod)
plt.show()
exit()
segments = cut_segments(time, eod, segment_length)
ampls = calculate_amplitudes(segments)

plt.hist(ampls)
plt.xlabel("amplitudes [mV]")
plt.ylabel("anzahl")
plt.show()
