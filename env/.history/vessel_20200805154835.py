import rigid_body as rb
class Vessel():

    def __init__(self):
        self.rigid_body = rb.RigidBody()
        self.added_mass = np.zeros(6,6)