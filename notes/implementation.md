Module system, so you can do

module = scl.component.init(world) 
alias_of[module.component1] # function for this?
world.assign(componentx, x)
componentx = world.lookup(module.x)

