"""
A simple example of an animated plot
"""
import sys
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib.animation as animation

gfname = sys.argv[1] # Generic file name
group  = sys.argv[2] # Atomic group
t0     = sys.argv[3] # Initial frame time [ps]

# Set up formatting for the movie files
Writer = animation.writers
writer = animation.FFMpegWriter(fps=15, metadata=dict(artist='Me'), bitrate=1800)

fig, ax = plt.subplots()
fname = group+'_PMEPot_'+group+'_'+t0+'-'+t0+'ps_'+gfname+'_eprofile.dat'
f		 = open(fname)
lines		 = f.readlines()
newlines	 = np.asarray([map(float, x.split())  for x in lines])
X0,Y0		 = newlines.T
line, = ax.plot(X0, Y0)

def animate(n):
    f = open("system_PMEPot_system_"+str(n)+'-'+str(n)+"ps_md_0mV_5ns_NVT_AfterPRMD_eprofile.dat")
    lines            = f.readlines()
    newlines         = np.asarray([map(float, x.split())  for x in lines])
    Xn,Yn            = newlines.T
    line.set_xdata(Xn)
    line.set_ydata(Yn)  # update the data
    return line,

ani = animation.FuncAnimation(fig, animate, np.arange(int(t0),5000, 10), interval=200, repeat_delay=2000)

ani.save('mymovie.mp4', writer=writer)

plt.show()
