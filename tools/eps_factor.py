#!/usr/bin/env python3
# from https://gist.github.com/adeebshihadeh/1a771a2e23fb06bbf2d8720abf71efa3
import sys
from tools.lib.logreader import LogReader

import numpy as np
from sklearn import linear_model


# get eps torque factor for toyotas

def to_signed(n, bits):
  if n >= (1 << max((bits - 1), 0)):
    n = n - (1 << max(bits, 0))
  return n


if __name__ == "__main__":
  if len(sys.argv) < 2:
    print("usage: {} rlog.bz2".format(sys.argv[0]))

  torque_cmd, eps_torque = 0, 0
  cmds, eps = [], []
  canmsgs = filter(lambda x: x.which() == "can", LogReader(sys.argv[1]))
  for can in canmsgs:
    update = False
    for msg in can.can:
      if msg.src == 128 and msg.address == 0x2e4:
        torque_cmd = to_signed((msg.dat[1] << 8) | msg.dat[2], 16)
        update = True
      elif msg.src == 0 and msg.address == 0x260:
        eps_torque = to_signed((msg.dat[5] << 8) | msg.dat[6], 16)
        update = True
    if update:
      cmds.append(torque_cmd)
      eps.append(eps_torque)

  start_idx = [i for i, v in enumerate(cmds) if v != 0][0]
  lm = linear_model.LinearRegression(fit_intercept=False)
  lm.fit(np.array(cmds[start_idx:]).reshape(-1, 1), eps[start_idx:])
  print(lm.coef_[0])
