import rigid_body as rb
import six_dof_actor
import numpy as np
# TODO: added mass interaction
# TODO: wave excitation force and torque
class Vessel(six_dof_actor.SixDOFActor):

    def __init__(self):
        super().__init__(self)
        self.rigid_body = rb.RigidBody()
        self.added_mass_matrix = np.zeros((6,6))
        self.first_order_damping_matrix = np.zeros((6,6))
        self.second_order_damping_matrix = np.zeros((6,6))
        self.restoring_matrix = np.zeros((6,6))

    def get_damping_force_and_torque(self):
        '''
        Return in world frame
        '''
        velocity_translational_model_frame, velocity_rotational_model_frame = self.rigid_body.get_velocity_model_frame()
        velocity_translational_and_rotational_model_frame = np.concatenate(velocity_translational_model_frame, velocity_rotational_model_frame) # questionable
        first_order_damping_force_and_torque = self.first_order_damping_matrix * velocity_translational_model_frame
        second_order_damping_force_and_torque = self.second_order_damping_matrix * np.multiply(velocity_translational_and_rotational_model_frame, velocity_translational_and_rotational_model_frame)
        total_damping_force_and_torque = first_order_damping_force_and_torque + second_order_damping_force_and_torque
        return -total_damping_force_and_torque[0:3], -total_damping_force_and_torque[3:6]
    
    def get_restoring_force_and_torque(self):
        '''
        Return in world frame
        '''
        yaw, pitch, roll = self.rotation.yaw_pitch_roll()
        return -self.restoring_matrix * np.array([self.position[0], self.position[1], self.position[2], roll, pitch, yaw])

    def update(self, dt : float):
        gravity_force = np.zeros(6)
        gravity_force[2] = self.rigid_body.get_gravitational_force(9.8)
        damping_force_and_torque = self.get_damping_force_and_torque()
        restoring_force_and_torque = self.get_restoring_force_and_torque()
        total_force_and_torque = damping_force_and_torque + restoring_force_and_torque + gravity_force
        
        self.rigid_body.advance(total_force_and_torque[0:3], total_force_and_torque[3:6], self.added_mass_matrix, dt)

        self.position = self.rigid_body.position
        self.rotation = self.rigid_body.rotation