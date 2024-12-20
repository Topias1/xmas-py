from bridge import Bridge
from animation import Animation

# Initialize the Bridge instance
bridge = Bridge()

# Initialize the Animation instance with the bridge and animation configuration file
animation = Animation(bridge, "animation.json")

# Launch the animation loop
animation.launch()