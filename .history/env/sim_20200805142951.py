class Sim:
    def __init__(self):
        self.isRunning = True
    
    def isRunning(self):
        return self.isRunning

sim = Sim()

while sim.isRunning():
    update()