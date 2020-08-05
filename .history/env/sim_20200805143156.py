class Sim():
    def __init__(self):
        self.running = True
        self.actor_list = []
        
    def isRunning(self):
        return self.running

    def update(self):
        print(1)

sim = Sim()

while sim.isRunning():
    sim.update()