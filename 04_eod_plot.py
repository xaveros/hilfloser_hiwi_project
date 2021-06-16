from nix_helpers import read_eod


time, eod = read_eod('../data/wave/2020-12-07-af-barometrix.nix/2020-12-07-af-barometrix.nix')

import matplotlib.pyplot as plt

plt.plot(time, eod)
plt.show()

