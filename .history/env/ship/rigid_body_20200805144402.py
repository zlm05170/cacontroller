import numpy as np
from pyquaternion import quaternion

class RigidBody():
    vector3 = np.array(shape = [3,1])
    def __init__(self):
        self.mass = 1 # kg
        self.center_of_gravity = np.zeros(3)
        self.moment_of_inertia = np.identity(3) #relative to cog
        self.position = np.zeros(3)
        self.rotation = quaternion.Quaternion()
    
    def update(self, external_force, external_torque)