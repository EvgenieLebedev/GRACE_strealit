import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Polygon


density_contrast_default = 500.0
x_zero = 50
x_scale = 100  
depth_zero = 200  
depth_scale = 100  
mgal_zero = 190  
mgal_scale = 10

# функция для расчета гравитационного потенциала
def talwani(x1, x2, z1, z2, density):
    G = 6.67e-11
    pi = np.pi
    epsilon = 1e-6  
    if x1 == 0:
        x1 += epsilon
    if x2 == 0:
        x2 += epsilon
    if (x2 - x1) == 0:
        x2 = x1 - epsilon
    denom = z2 - z1
    if denom == 0:
        denom = epsilon
    alpha = (x2 - x1) / denom
    beta = (x1 * z2 - x2 * z1) / denom
    factor = beta / (1 + alpha * alpha)
    r1sq = (x1 * x1 + z1 * z1)
    r2sq = (x2 * x2 + z2 * z2)
    term1 = 0.5 * (np.log(r2sq) - np.log(r1sq))
    term2 = np.arctan2(z2, x2) - np.arctan2(z1, x1)
    zz = factor * (term1 - alpha * term2)
    grav = 2 * G * density * zz * 1e5
    return -grav  

