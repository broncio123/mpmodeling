import sys

pdb0 = sys.argv[1] # Narrow model
#pdb1 = sys.argv[2] # Wide model
#output = sys.argv[3] # PNG output filename

cmd.load(pdb0,'model0')
#cmd.load(pdb1,'model1')

cmd.bg_color("white")
cmd.set("orthoscopic")
cmd.hide("lines")
cmd.rotate("x",-90)

Colors = {1:"marine", 0:"green"}
Surf_alpha = {0:0.85, 1:0.85}
Sphere_alpha = {0:0.1, 1:0.1}
chain_sel = "g+c"
myview = (0.1379110962152481, 
	0.08135918527841568, 
	-0.9870973825454712, 
	-0.05711836367845535, 
	0.9956154823303223, 
	0.07408057898283005, 
	0.9887959361076355, 
	0.0461648553609848, 
	0.1419534832239151, 
	0.0, 
	0.0, 
	-164.69821166992188, 
	-0.2233104705810547, 
	1.266448974609375, 
	-5.080259323120117, 
	129.8493194580078, 
	199.54710388183594, 
	20.0)
cmd.set_view(myview)

for i in [0]:
	cmd.create("chains"+str(i),"model"+str(i)+" and chain "+chain_sel)
	cmd.color(Colors[i],"chains"+str(i)+" and name C*")
	#
	cmd.show("sphere","chains"+str(i)+" and resn TYR+CYS")
	cmd.set("sphere_transparency",Sphere_alpha[i],"chains"+str(i))
	#
	cmd.show("cartoon","chains"+str(i))
	cmd.show("surf","chains"+str(i))
	#
	cmd.set("surface_color",Colors[i],"chains"+str(i))
	cmd.set("transparency",Surf_alpha[i],"chains"+str(i))

cmd.set("ray_orthoscopic")
cmd.set("transparency_mode",1)
cmd.set("ray_opaque_background",1)
#cmd.ray(2400,2400)
#cmd.png(output)

