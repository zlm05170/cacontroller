import sim
import vessel

scene = sim.Sim()

scene.add_actor(vessel.Vessel())

scene.run()