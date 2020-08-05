class Sim():
    def __init__(self):
        self.running = True
    
    def isRunning(self):
        return self.running

    def update(self):
        print(1)

sim = Sim()

while sim.isRunning():
    update()