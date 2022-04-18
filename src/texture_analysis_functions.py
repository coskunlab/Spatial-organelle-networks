import numpy as np
import pandas as pd
import skimage
from skimage.filters import laplace, sobel, sobel_h, sobel_v
from scipy.spatial import distance
from scipy.cluster import hierarchy
from scipy.signal import convolve2d

# Functions to calculate texture features

def energy_laplacian(image):
    laplace_temp = laplace(image)
    return(laplace_temp * laplace_temp)

def modified_laplacian(image):
    M, N = image.shape

    Lx = np.array([1, -2, 1]).reshape(-1, 1)
    Ly = Lx.T
    image_Lx = np.abs(convolve2d(image, Lx))
    image_Ly = np.abs(convolve2d(image, Ly))
    image_m = image_Lx[1:M+1] + image_Ly[:, 1:N+1]
    return(image_m)

def diagonal_laplacian(image):
    M, N = image.shape

    Lx = np.array([1, -2, 1]).reshape(-1, 1)
    Ly = Lx.T
    Lx1 = 1/np.sqrt(2) * np.array([[0, 0, 1],
                                   [0, -2, 0],
                                   [1, 0, 0]])
    Lx2 = 1/np.sqrt(2) * np.array([[1, 0, 0],
                                   [0, -2, 0],
                                   [0, 0, 1]])
    
    image_Lx = np.abs(convolve2d(image, Lx))
    image_Ly = np.abs(convolve2d(image, Ly))
    image_Lx1 = np.abs(convolve2d(image, Lx1))
    image_Lx2 = np.abs(convolve2d(image, Lx2))
    
    image_m = image_Lx[1:M+1] + image_Ly[:, 1:N+1] + image_Lx1[1:M+1, 1:N+1] + image_Lx2[1:M+1, 1:N+1]
    return(image_m)

def variance_laplacian(image):
    laplace_temp = laplace(image)
    laplace_temp_mean = laplace_temp.mean()
    return((laplace_temp - laplace_temp_mean) * (laplace_temp - laplace_temp_mean))

def gray_level_variance(image):
    mu = np.mean(image)
    return((image - mu) * (image - mu))

def tenengrad(image):
    Gx = sobel_h(image)
    Gy = sobel_v(image)
    image_tenen_sqrt = (Gx * Gx) + (Gy * Gy)
    return(image_tenen_sqrt * image_tenen_sqrt)

