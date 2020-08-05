import numpy as np
from pyquaternion import quaternion

class RigidBody():

    def __init__(self):
        self.mass = 1 # kg
        self.center_of_gravity = np.zeros(3)
        self.moment_of_inertia = np.identity(3) #relative to cog
        self.position = np.zeros(3)
        self.rotation = quaternion.Quaternion()
        self.velocity = np.zeros(3)
        self.rotational_velocity = np.zeros(3)

    def update(self, external_force, external_torque, dt):
        '''
        external_force is in world frame, relative to model origin
        external_torque is in world frame, relative to model origin
        '''
        