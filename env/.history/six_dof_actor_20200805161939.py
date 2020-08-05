import actor
import numpy as np
from pyquaternion import quaternion
class SixDOFActor(actor.Actor):

    def __init__(self):
        super().__init__(self)
        self.position = np.zeros(3)
        self.rotation = quaternion.Quaternion()