from operator import pos
import numpy as np
from pyquaternion import quaternion

class RigidBody:

    def __init__(self):
        self.mass = 1 # kg
        self.center_of_gravity = np.zeros(3)
        self.moment_of_inertia = np.identity(3) #relative to cog
        self.position = np.zeros(3)
        self.rotation = quaternion.Quaternion()
        self.velocity = np.zeros(3) # world frame
        self.rotational_velocity = np.zeros(3) # world frame

    def get_velocity_model_frame(self):
        return self.rotation.inverse.rotate(self.velocity), self.rotation.inverse.rotate(self.rotational_velocity)

    def get_gravitational_force(self, gravitational_acceleration):
        return self.mass * gravitational_acceleration
    
    def get_paralleled_moment_of_inertia(self, arm, moment_of_inertia_cog_frame):
        return moment_of_inertia_cog_frame + (np.dot(arm, arm)*np.identity(3) - np.outer(arm, arm)) * self.mass
    
    def get_smtrx(self, v):
        return np.array([0, -v[2], v[1]],
                        [v[2], 0, -v[0]],
                        [-v[1], v[0], 0])

    def advance(self, external_force_world_frame, external_torque_world_frame, added_mass_matrix_6x6 = np.zeros((6,6)), dt):
        '''
        external_force is in world frame, relative to model origin
        external_torque is in world frame, relative to model origin
        '''
        # Get external force & torque in model frame
        world_to_model = self.rotation.inverse
        external_force_model_frame = world_to_model.rotate(external_force_world_frame)
        external_torque_model_frame = world_to_model.rotate(external_torque_world_frame)
        
        # Set up 6x6 inertia matrix in model frame
        inertia_matrix_6x6 = np.zeros((6,6))
        inertia_matrix_6x6[0:3, 0:3] = np.identity(3) * self.mass
        inertia_matrix_6x6[3:6, 3:6] = self.get_paralleled_moment_of_inertia(-self.center_of_gravity, self.moment_of_inertia)
        inertia_matrix_6x6[0:3, 3:6] = self.get_smtrx(self.center_of_gravity) * self.mass
        inertia_matrix_6x6[3:6, 0:3] = -inertia_matrix_6x6[0:3, 3:6]
        acceleration_translational_and_rotational_model_frame = np.inverse(inertia_matrix_6x6 + added_mass_matrix_6x6) * np.concatenate(external_force_model_frame, external_torque_model_frame)
        
        # # Get external force & torque in cog frame
        # external_force_cog_frame = external_force_model_frame
        # external_torque_cog_frame = external_torque_model_frame + np.cross(self.cog, external_force_model_frame)

        # # Get acceleration in cog frame
        # acceleration_translational_cog_frame = 1/ self.mass * external_force_cog_frame
        # acceleration_rotational_cog_frame = np.inverse(self.moment_of_inertia) * external_torque_cog_frame

        # # Get acceleration in world frame, relative to cog
        # acceleration_translational_world_frame = self.rotation.rotate(acceleration_translational_cog_frame)
        # acceleration_rotational_world_frame = self.rotation.rotate(acceleration_rotational_cog_frame) + np.cross(self.rotational_velocity, self.velocity)
        
        # Get acceleration in world frame, relative to model origin
        acceleration_translational_world_frame = self.rotation.rotate(acceleration_translational_and_rotational_model_frame[0:3])
        acceleration_rotational_world_frame = self.rotation.rotate(acceleration_translational_and_rotational_model_frame[3:6]) + np.cross(self.rotational_velocity, self.velocity)

        # Integrate acceleration to get velocity in world frame, relative to model origin
        velocity_translational_world_frame = self.velocity + acceleration_translational_world_frame * dt
        velocity_rotational_world_frame = self.rotational_velocity + acceleration_rotational_world_frame * dt

        # Integrate velocity to get position and rotation
        self.position = self.position + + velocity_translational_world_frame * dt
        velocity_rotational_model_frame = world_to_model.rotate(velocity_rotational_world_frame)
        self.rotation = quaternion.Quaternion.sym_exp_map(self.rotation, velocity_rotational_model_frame * dt) # questionable