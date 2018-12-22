
import itertools
import more_itertools
import numpy
from operator import itemgetter

def split_vdw_profile(primitive_profile, vdw_profile):
    X_p,Y_p = primitive_profile
    X_vdw,Y_vdw = vdw_profile
    N_vdw = len(X_vdw)
    # Redefine primitive profile
    ## X-coords
    n_end = 10
    X_p_left_end = list(numpy.linspace(min(X_vdw),X_p[0],n_end))
    X_p_right_end = list(numpy.linspace(max(X_vdw),X_p[-1],n_end))
    X_p = X_p_left_end + X_p + X_p_right_end
    ## Y-coords
    Y_p_left_end = list(Y_p[0]*numpy.ones(n_end))
    Y_p_right_end = list(Y_p[-1]*numpy.ones(n_end))
    Y_p = Y_p_left_end + Y_p + Y_p_right_end

    # Get product of sets of indices for data points of each profile
    indices_p = list(range(len(X_p)))
    indices_vdw = list(range(len(X_vdw)))
    indices_product = list(itertools.product(indices_p,indices_vdw))

    # Get sets of 2D vectors from both profiles
    XY_p = numpy.array([X_p, Y_p]).T
    XY_vdw = numpy.array([X_vdw, Y_vdw]).T
    
    # Pairwise distances between points from different sets
    dist_p_vdw = [(numpy.linalg.norm(XY_p[i] - XY_vdw[j]),(i,j)) for i,j in indices_product]
    dist_p_vdw = sorted(dist_p_vdw, key=itemgetter(0)) ## Sort by first distance; low to high

    # Extract indices for points with minimum distance
    indx_p0, indx_vdw0 = dist_p_vdw[0][-1]
    for i in range(len(dist_p_vdw)):
        indx_p, indx_vdw = dist_p_vdw[i][-1]
        if abs(indx_p - indx_p0)>10:
            # Index points must be distant 
            break
    
    # Index range: first half VdW profile
    indx_range0 = list( range( min(indx_vdw0, indx_vdw), max(indx_vdw0, indx_vdw) ) )
    # Index range: second half VdW profile
    indx_range1 = list( set(list(range(N_vdw))) - set(indx_range0) )
    indx_range1 = sorted( indx_range1 )
    
    vdw_profile0 = [itemgetter(*indx_range0)(X_vdw), itemgetter(*indx_range0)(Y_vdw)]
    vdw_profile1 = [itemgetter(*indx_range1)(X_vdw), itemgetter(*indx_range1)(Y_vdw)]
    ###########################  REDEFINE PROFILE 1
    iterable = indx_range1
    indx_range10, indx_range11 = [list(group) for group in more_itertools.consecutive_groups(iterable)]

    X_vdw_range10 = itemgetter(*indx_range10)(X_vdw)
    X_vdw_range11 = itemgetter(*indx_range11)(X_vdw)

    if numpy.mean(X_vdw_range10) < numpy.mean(X_vdw_range11):
        X1_vdw_left = X_vdw_range10
        Y1_vdw_left = itemgetter(*indx_range10)(Y_vdw)

        X1_vdw_right = X_vdw_range11
        Y1_vdw_right = itemgetter(*indx_range11)(Y_vdw)
    else:
        X1_vdw_left = X_vdw_range11
        Y1_vdw_left = itemgetter(*indx_range11)(Y_vdw)

        X1_vdw_right = X_vdw_range10
        Y1_vdw_right = itemgetter(*indx_range10)(Y_vdw)
    #####################################################################
    base_transf = ['normal','reverse']
    transf_combination = list(itertools.product(base_transf, base_transf))

    def apply_transf(X, transf):
        if transf == 'normal':
            return list(X)
        elif transf == 'reverse':
            return list(reversed(X))

    for transf_L, transf_R in transf_combination:
        S_left = apply_transf(X1_vdw_left,transf_L)
        S_right = apply_transf(X1_vdw_right,transf_R)

        start_left = S_left[0]
        end_left = S_left[-1]

        start_right = S_right[0]
        end_right = S_right[-1]

        if abs(end_left - start_right) < 1:
            X1_vdw_left = S_left
            X1_vdw_right = S_right
            Y1_vdw_left = apply_transf(Y1_vdw_left,transf_L)
            Y1_vdw_right = apply_transf(Y1_vdw_right,transf_R)
            X1_vdw = X1_vdw_left + X1_vdw_right
            Y1_vdw = Y1_vdw_left + Y1_vdw_right
            break
    vdw_profile1 = [list(X1_vdw), list(Y1_vdw)]
    #####################################################################
    if numpy.mean(list(vdw_profile1[1])) > numpy.mean(list(vdw_profile0[1])):
        lower_vdw_profile = vdw_profile0
        upper_vdw_profile = vdw_profile1
        return lower_vdw_profile, upper_vdw_profile
    else:
        lower_vdw_profile = vdw_profile1
        upper_vdw_profile = vdw_profile0
        return lower_vdw_profile, upper_vdw_profile
    
if __name__ == "__main__":
    pass