import numpy as np
import scipy.special as sp
import src.library.coplanar_coupler as coupler
import os
import pickle

"""
File containing resonator utility methods, e.g. kinetic inductance, TL couplings and resonator lengths
"""

#############
# Constants #
#############

eps_0 = 8.8541878128e-12
mu_0 = 1.25663706212e-6
c = 2.99792458e8

################
# Lkin methods #
################

def k_0(w, g) -> float:
    """
    k_0 parameter
    @param w: width of the CPW
    @param g: gap of the CPW
    @return: k_0
    """
    return w/(w+2*g)


def k_0_prime(w, g) -> float:
    """
    k_0' parameter
    @param w: width of the CPW
    @param g: gap of the CPW
    @return: k_0'
    """
    return np.sqrt(1-k_0(w, g)**2)


def K(k) -> float:
    """
    Complete elliptic integral of the first kind
    @param k: parameter for the integral
    @return: value of K(k)
    """
    return sp.ellipk(k**2)  # beware: scipy returns K(m), not K(k) -> return K(k**2), as m == k**2!


def C_geo(w, g, eps_eff) -> float:
    """
    Geometric capacitance per length of a CPW
    @param w: width
    @param g: gap
    @param eps_eff: effective permittivity
    @return: geometric capacitance per length
    """
    return 4*eps_0*eps_eff*K(k_0(w, g))/K(k_0_prime(w, g))


def L_geo(w, g) -> float:
    """
    Geometric inductance per length of a CPW
    @param w: width
    @param g: gap
    @return: geometric inductance per length
    """
    return mu_0/4*K(k_0_prime(w, g))/K(k_0(w, g))


def L_kin_raw(w, g, t, lambda_0) -> float:
    """
    Raw kinetic inductance per length (not considering CPW)
    @param w: width
    @param g: gap
    @param t: thickness of the film
    @param lambda_0: london penetration depth of the film material
    @return: raw kinetic inductance
    """
    return 1/(w*t)*mu_0*lambda_0**2


def L_kin(w, g, t, lambda_0) -> float:
    """
    Kinetic inductance per length of a CPW
    @param w: width
    @param g: gap
    @param t: thickness of the film
    @param lambda_0: london penetration depth of the film material
    @return: kinetic inductance of the CPW
    """
    if t > 2*lambda_0:
        t = 2*lambda_0  # effective thickness of twice the penetration depth
    return L_kin_raw(w, g, t, lambda_0)/(2*k_0(w, g)**2*K(k_0(w, g))**2)*(-np.log(t/(4*w))-k_0(w, g)*np.log(t/(4*(w+2*g)))+2*(w+g)/(w+2*g)*np.log(g/(w+g)))


#########################
# TL-Resonator coupling #
#########################

def calc_coupling_length(width_cpw, gap_cpw, width_res, gap_res, coupling_ground, length, q_ext, eps_eff) -> float:
    """
    Calculates the needed coupling length for achieving a given Q factor. Assuming all lengths in nanometres
    For reference, see https://doi.org/10.1140/epjqt/s40507-018-0066-3
    :@param l_res: length of the resonator
    :@param intended_q: external Q one wishes to achieve
    :@return: The calculated coupling length
    """
    key = (width_cpw, gap_cpw, width_res, gap_res,
           coupling_ground, eps_eff)

    kappa_dict = _load_kappa_dict()

    if key in kappa_dict:
        kappa = kappa_dict[key]
    else:
        print("No value for kappa detected. Calculating new value for determining Q_ext...")
        cpw_c = coupler.coplanar_coupler()
        cpw_c.w1 = width_cpw
        cpw_c.s1 = gap_cpw
        cpw_c.w2 = width_res
        cpw_c.s2 = gap_res
        cpw_c.w3 = coupling_ground
        cpw_c.epsilon_eff = 6.45
        Cl, Ll, Zl = cpw_c.coupling_matrices(mode='notch')
        kappa = Zl[0, 1] / (np.sqrt(Zl[0, 0] * Zl[1, 1]))

        kappa_dict[key] = kappa
        _save_kappa_dict(kappa_dict)

    return int((_v_ph(eps_eff) / (2 * np.pi * calc_f0(length, eps_eff) * 1e9) * np.arcsin(
        np.sqrt(np.pi / (2 * kappa ** 2 * q_ext)))) * 1e9)


def calc_f0(length, eps_eff) -> float:
    """
    Calculate a rough estimate for f0. Assuming Si-Air boundary and a lambda/4 resonator.
    :@param length: The length of the resonator in nanometres
    :@return: The resonance frequency in GHz
    """
    return _v_ph(eps_eff) / (4 * length * 1e-9) * 1e-9


def calc_length(f0, eps_eff) -> float:
    """
    Calculate a rough estimate for the length. Assuming a lambda/4 resonator.
    :@param f0: The resonance frequency in GHz
    :@param eps_eff: The effective permittivity
    :@return: The length of the resonator in nanometres
    """
    return _v_ph(eps_eff) / (4 * f0 * 1e9) * 1e9


def _v_ph(eps_eff) -> float:
    """
    Get the phase velocity in dependence of the effective epsilon
    @return: effective phase velocity of light
    """
    return c / np.sqrt(eps_eff)


def _load_kappa_dict() -> {(float, float, float, float, float): float}:
    """
    Load the kappa dictionary for fast calculation of the Quality factor
    @return: Dictionary containing the parameters and associated kappa value
    """
    if not os.path.exists('../../kappaValues.txt'):
        _save_kappa_dict({(10, 6, 10, 6, 3, 6.45): 0.11358238085799895})
    with open('../../kappaValues.txt', 'rb') as handle:
        return pickle.loads(handle.read())


def _save_kappa_dict(kappa_dict):
    """
    Save the kappa dictionary into a binary (non-readable) file
    @param kappa_dict: Dictionary to save
    """
    with open('../../kappaValues.txt', 'wb') as handle:
        pickle.dump(kappa_dict, handle)
