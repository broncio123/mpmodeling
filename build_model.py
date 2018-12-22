import os, numpy, sys
import isambard_dev

N_chains	= int(sys.argv[1])
sequence	= str(sys.argv[2])
radius		= float(sys.argv[3])
pitch		= float(sys.argv[4])
phica		= float(sys.argv[5])
outfile		= str(sys.argv[6])

model = isambard_dev.ampal.specifications.CoiledCoil.from_parameters(N_chains,len(sequence),radius,pitch,phica)
model.build()
model.pack_new_sequences((sequence)*N_chains)
with open(outfile, 'w') as x: 
    x.write(model.pdb)

print("BUFF score: Model")
print(model.buff_interaction_energy)


