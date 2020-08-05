import actor
from pyquaternion import Quaternion
class SixDOFActor(actor.Actor):

    def __init__(self):
        super().__init__(self)
        self.position = np.zeros(3)
        self.rotation = 