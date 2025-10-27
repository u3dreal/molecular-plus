# Matter descriptions
MATTER_CUSTOM = "put your parameter below"
MATTER_SAND = "1555kg per meter cu"
MATTER_WATER = "1000kg per meter cu"
MATTER_IRON = "7800kg per meter cu"

# Properties descriptions
ACTIVE = "Activate molecular script for this particles system"
REFRESH = "Simple property used to refresh data in the process"

DENSITY_ACTIVE = "Control particle weight by density"
MATTER = "Choose a matter preset for density"
DENSITY = "Density of the matter kg/cube meter"

SELF_COLLISION_ACTIVE = "Activate self collsion between particles in the system"
OTHER_COLLISION_ACTIVE = "Activate collision with particles from others systems"
FRICTION = "Friction between particles at collision 0 = no friction , 1 = full friction"
COLLISION_DAMPING = (
    "Damping between particles at collision 0 = bouncy , 1 = no collision"
)
COLLISION_ADHESION_SEARCH_DISTANCE = (
    "Distance to search for adhesion particles relative to particles radius"
)
COLLISION_ADHESION_FACTOR = "Factor to multiply the adhesion force"
COLLISION_GROUP = "Choose a collision group you want to collide with"

LINKS_ACTIVE = "Activate links between particles of this system"
LINK_OTHER_ACTIVE = ""
LINK_GROUP = ""
LINK_RELATIVE_LENGTH = "Activate search distance relative to particles radius"
LINK_FRICTION = "Friction in links , a kind of viscosity. Slow down tangent velocity. 0 = no friction , 1.0 = full of friction"
LINK_LENGTH = "Searching range to make a link between particles"
LINK_TENSION = "Make link bigger or smaller than it's created (1 = normal , 0.9 = 10% smaller , 1.15 = 15% bigger)"
LINK_TENSION_RANDOM = "Tension random"
LINK_MAX = "Maximum of links per particles"
LINK_STIFFNESS = "Stiffness of links between particles"
LINK_STIFFNESS_RANDOM = "Random variation for stiffness"
LINK_STIFFNESS_EXPONENT = "Give a exponent force to the spring links"
LINK_DAMPING = "Damping effect on spring links"
LINK_DAMPING_RANDOM = "Random variation on damping"
LINK_BROKEN = "How much link can stretch before they broken. 0.01 = 1% , 0.5 = 50% , 2.0 = 200% ..."
LINK_BROKEN_RANDOM = "Give a random variation to the stretch limit"
LINK_SAME_VALUE = (
    "When active , expansion and compression of the spring have same value"
)
LINK_EXPENSION_STIFFNESS = "Expension stiffness of links between particles"
LINK_EXPENSION_STIFFNESS_RANDOM = "Random variation for expansion stiffness"
LINK_EXPENSION_STIFFNESS_EXPONENT = (
    "Give a exponent force to the expension spring links"
)
LINK_EXPENSION_DAMPING = "Damping effect on expension spring links"
LINK_EXPENSION_DAMPING_RANDOM = "Random variation on expension damping"
LINK_EXPENSION_BROKEN = "How much link can expand before they broken. 0.01 = 1% , 0.5 = 50% , 2.0 = 200% ..."
LINK_EXPENSION_BROKEN_RANDOM = "Give a random variation to the expension stretch limit"

RELINK_GROUP = "Choose a group that new link are possible"
RELINK_CHANCE = (
    "Chance of a new link are created on collision. 0 = off , 100 = 100% of chance"
)
RELINK_CHANCE_RANDOM = "Give a random variation to the chance of new link"
RELINK_TENSION = "Make link bigger or smaller than it's created (1 = normal , 0.9 = 10% smaller , 1.15 = 15% bigger)"
RELINK_TENSION_RANDOM = "Tension random"
RELINK_MAX = "Maximum of links per particles"
RELINK_STIFFNESS = "Stiffness of links between particles"
RELINK_STIFFNESS_RANDOM = "Random variation for stiffness"
RELINK_STIFFNESS_EXPONENT = "Give a exponent force to the spring links"
RELINK_DAMPING = "Damping effect on spring links"
RELINK_DAMPING_RANDOM = "Random variation on damping"
RELINK_BROKEN = "How much link can stretch before they broken. 0.01 = 1% , 0.5 = 50% , 2.0 = 200% ..."
RELINK_BROKEN_RANDOM = "Give a random variation to the stretch limit"
RELINK_SAME_VALUE = (
    "When active , expansion and compression of the spring have same value"
)
RELINK_EXPENSION_STIFFNESS = "Stiffness of links expension between particles"
RELINK_EXPENSION_STIFFNESS_RANDOM = "Random variation for expension stiffness"
RELINK_EXPENSION_STIFFNESS_EXPONENT = "Give a exponent force to the spring links"
RELINK_EXPENSION_DAMPING = "Damping effect on expension spring links"
RELINK_EXPENSION_DAMPING_RANDOM = "Random variation on damping"
RELINK_EXPENSION_BROKEN = "How much link can stretch before they broken. 0.01 = 1% , 0.5 = 50% , 2.0 = 200% ..."
RELINK_EXPENSION_BROKEN_RANDOM = "Give a random variation to the stretch limit"

VAR_1 = "Current number of particles to calculate substep"
VAR_2 = "Current substep"
VAR_3 = "Targeted number of particles you want to increase or decrease from current system to calculate substep you need to achieve similar effect"
BAKE_UV = "Bake UV upon finish"

TIME_SCALE_ACTIVE = "Use custom Timescale"
TIME_SCALE = "Speed up or Slow down the simulation with this multiplier"
SUBSTEP = "More steps equals more stable and accurate results, but is slower"
BAKE = "Bake simulation when finish"
RENDER = "Start rendering animation when simulation is finish. WARNING: It's freeze blender until render is finish"
CPU = "Numbers of thread's included to process the simulation"
