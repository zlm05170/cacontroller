import math
import numpy as np
import simulate, addEvent

class run(object):
    def __init__(self):
        self.a = simulate.ship_model()
        self.b = addEvent.event
        self.Event = np.array([0,0])
        self.RPM_CMD = 0
        self.alfa_c = 0/180*np.pi
        self.V_w = 0
        self.beta_w =0/180*np.pi
        self.x0 = np.array([0,0,0,5.77,0,0])
        self.t0 = 0
        self.t1 = 200
        self.h = 0.2

    def run_sim(self):
        


if __name__ == "__main__"
    run_sim()

