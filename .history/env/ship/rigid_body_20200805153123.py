import numpy as np
from pyquaternion import quaternion

class RigidBody():

    def __init__(self):
        self.mass = 1 # kg
        self.center_of_gravity = np.zeros(3)
        self.moment_of_inertia = np.identity(3) #relative to cog
        self.position = np.zeros(3)
        self.rotation = quaternion.Quaternion()
        self.velocity = np.zeros(3) # world frame
        self.rotational_velocity = np.zeros(3) # world frame

    def get_cog_position(self):
        '''
        Get cog position in world frame
        '''
        return self.position + self.rotation.rotate(self.center_of_gravity)

    def advance(self, external_force_world_frame, external_torque_world_frame, dt):
        '''
        external_force is in world frame, relative to model origin
        external_torque is in world frame, relative to model origin
        '''
        # Get external force & torque in model frame
        world_to_model = self.rotation.inverse
        external_force_model_frame = world_to_model.rotate(external_force_world_frame)
        external_torque_model_frame = world_to_model.rotate(external_torque_world_frame)
        
        # Get external force & torque in cog frame
        external_force_cog_frame = external_force_model_frame
        external_torque_cog_frame = external_torque_model_frame + np.cross(self.cog, external_force_model_frame)

        # Get acceleration in cog frame
        acceleration_translational_cog_frame = 1/ self.mass * external_force_cog_frame
        acceleration_rotational_cog_frame = np.inverse(self.moment_of_inertia) * external_torque_cog_frame

        # Get acceleration in world frame, relative to cog
        acceleration_translational_world_frame = self.rotation.rotate(acceleration_translational_cog_frame)
        acceleration_rotational_world_frame = self.rotation.rotate(acceleration_rotational_cog_frame) + np.cross(self.rotational_velocity, self.velocity)

        # Integrate acceleration to get velocity
        velocity_translational_world_frame = self.velocity + acceleration_translational_world_frame * dt
        velocity_rotational_world_frame = self.rotational_velocity + acceleration_rotational_world_frame * dt

        # Integrate velocity to get position and rotation
        position_cog =  self.get_cog_position() + velocity_translational_world_frame * dt
        velocity_rotational_cog_frame = world_to_model.rotate(velocity_rotational_world_frame)
        self.rotation = quaternion.Quaternion.sym_exp_map(self.rotation, velocity_rotational_cog_frame * dt) # questionable