
import numpy, sys
lines   = sys.stdin.readlines()
V	= float(sys.argv[1])
icharge = []
time    = []
for l in lines:
	a,b,c = map(float, l.split())
	time.append(a)
	icharge.append(b-c)
icharge =  numpy.cumsum(icharge)
I = (1.6E-19)*numpy.polyfit(time, icharge, 1)[0] / float(1E-12)
print( V, I, numpy.abs(float(I)/float(V)))

