from operator import itemgetter

def find_vdw_minima(chain_profile, profile_per_residue_data, Rmin_tol = 1):
    X,Y = chain_profile
    Rmin_global = min(Y)
    ################################
    data_model = []
    for profile_data in profile_per_residue_data:
        res, resn, profile = profile_data
        sorted_profile = sorted(profile.T, key=itemgetter(1) )
        Z,R = sorted_profile[0]
        if abs(R - Rmin_global) <= Rmin_tol:
            data_model.append([Z,R,res,resn])
    data_model_sorted = sorted(data_model, key=itemgetter(1))
    return data_model_sorted

if __name__ == "__main__":
    pass