class Sim():
    def __init__(self):
        self.isRunning = True
    
    def isRunning(self):
        return self.isRunning

    def update(self):
        print(1)
        
sim = Sim()

while sim.isRunning():
    update()