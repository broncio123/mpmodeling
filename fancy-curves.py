#!/usr/bin/env python

import numpy as np
import matplotlib.pyplot as plt
import sys

def errorfill(x, y, yerr, color=None, alpha_fill=0.3, ax=None):
    ax = ax if ax is not None else plt.gca()
    if color is None:
        color = ax._get_lines.color_cycle.next()
    if np.isscalar(yerr) or len(yerr) == len(y):
        ymin = y - yerr
        ymax = y + yerr
    elif len(yerr) == 2:
        ymin, ymax = yerr
    ax.plot(x, y, color=color, linewidth=2)
    ax.fill_between(x, ymax, ymin, color=color, alpha=alpha_fill)
    ax.set_xlim([0,25000])

def running_average(X, bins):
	N=len(X)
	New_X = []
	for n in range(0,N,bins): 
		New_X.append(np.mean(X[n:n+bins]))
	return np.array(New_X)

def total_dispersion(X, bins):
	N=len(X)
        New_X = []
        for n in range(0,N,bins):
                New_X.append(np.sqrt( np.sum( map(lambda x: x**2, X[n:n+bins]) ) ) )
        return np.array(New_X)

lines = sys.stdin.readlines()
Data={}
block=0
X=[]; Y=[]; dY=[]
for l in lines:
	if "&" not in l:
		x, y, dy = map(float, l.split())
		X.append(x)  
		Y.append(y)
		dY.append(dy)
	else:
		Data[block] = np.array([X,Y,dY])
		X=[]; Y=[]; dY=[]
		block+=1

for n in range(len(Data.keys())):
	bins=10
	X=Data[n][0][0::bins]
	mY = running_average(Data[n][1], bins)
	tdY = total_dispersion(Data[n][2], bins)    
	errorfill(X,mY,tdY)
plt.savefig("test1.png")
plt.show()
	
