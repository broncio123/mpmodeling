
pdb=sys.argv[1]

cmd.load(pdb,"MyProtein")
cmd.select("myres","res 32 and name O1")
cmd.alter("myres",'name="O"')
cmd.save(pdb,"MyProtein")

