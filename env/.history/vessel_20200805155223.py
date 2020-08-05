import rigid_body as rb
import actor
import numpy as np

class Vessel(actor.Actor):

    def __init__(self):
        self.rigid_body = rb.RigidBody()
        self.added_mass_matrix = np.zeros((6,6))
        self.first_order_damping_matrix = np.zeros((6,6))
        self.second_order_damping_matrix = np.zeros((6,6))

    