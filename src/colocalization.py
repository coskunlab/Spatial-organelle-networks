import numpy as np
from math import log10, sqrt, ceil, floor, log, exp, pi, isnan
import pandas as pd

# Functions to calculate Pearson's correlation

def generate_pearson_metric_masked(img1, img2):    

    df_img = pd.DataFrame({'CH1':img1.copy().ravel(),'CH2':img2.copy().ravel()}, dtype=np.float64)

    number_pixel = img1.copy().ravel().shape[0]
    df_img_masked = df_img
    df_img_masked = df_img_masked[["CH1", "CH2"]]    
    
    ############################################
    pearson = df_img_masked.copy().corr("pearson")["CH1"][1]
    
    if isnan(pearson):
        pearson = 0.0
    
    del df_img_masked

    ############################################
    return(pearson)


   
def multi_generate_colo_metric_masked(img1, img2):    

    df_img = pd.DataFrame({'CH1':img1.copy().ravel(),'CH2':img2.copy().ravel()}, dtype=np.float64)

    number_pixel = img1.copy().ravel().shape[0]
    df_img_masked = df_img
    df_img_masked = df_img_masked[["CH1", "CH2"]]    
    
    ############################################
    pearson = df_img_masked.copy().corr("pearson")["CH1"][1]
    kendall = df_img_masked.copy().corr("kendall")["CH1"][1]
    spearman = df_img_masked.copy().corr("spearman")["CH1"][1]
    
    if isnan(pearson):
        pearson = 0.0
    
    if isnan(kendall):
        kendall = 0.0
        
    if isnan(spearman):
        spearman = 0.0

    ############################################
    threshold_m_10 = df_img_masked.quantile(0.1)

    if threshold_m_10[0] == 0. or isnan(threshold_m_10[0]):
        threshold_m_10[0] = 0.0001
    if threshold_m_10[1] == 0. or isnan(threshold_m_10[1]):
        threshold_m_10[1] = 0.0001
    
    df_img_masked.loc[df_img_masked['CH1'] <= threshold_m_10[0] , 'CH1_M'] = 0.0
    df_img_masked.loc[df_img_masked['CH1'] > threshold_m_10[0] , 'CH1_M'] = 1.0

    df_img_masked.loc[df_img_masked['CH2'] <= threshold_m_10[1] , 'CH2_M'] = 0.0
    df_img_masked.loc[df_img_masked['CH2'] > threshold_m_10[1] , 'CH2_M'] = 1.0
    
    df_img_masked["union"] = df_img_masked["CH1_M"] * df_img_masked["CH2_M"]
    
    df_img_masked_sum = df_img_masked.sum()

    ch1_sum = df_img_masked_sum["CH1_M"]
    ch2_sum = df_img_masked_sum["CH2_M"]
    union_sum = df_img_masked_sum["union"]
    
    if ch1_sum == 0.:
        M1 = 0.
    else:
        M1 = union_sum / ch1_sum
    
    if ch2_sum == 0.:
        M2 = 0.
    else:
        M2 = union_sum / ch2_sum
    
    ############################################
    
    df_img_mean = df_img_masked.mean()
    mean_CH1 = df_img_mean["CH1"]
    mean_CH2 = df_img_mean["CH2"]
    # print(mean_CH1, mean_CH2)
    df_img_masked["CH1-mean"] = (df_img_masked["CH1"] - mean_CH1)
    df_img_masked["CH2-mean"] = (df_img_masked["CH2"] - mean_CH2)
    
    df_img_masked["ICQ_voxel"] = df_img_masked["CH1-mean"] * df_img_masked["CH2-mean"]
    df_img_masked.loc[df_img_masked['ICQ_voxel'] < 0.0 , 'ICQ_voxel_sign'] = 0.0
    df_img_masked.loc[df_img_masked['ICQ_voxel'] >= 0.0 , 'ICQ_voxel_sign'] = 1.0
    
    df_img_masked['ICQ_voxel_sign_final'] = df_img_masked["ICQ_voxel_sign"]
    df_img_sum = df_img_masked.sum()
    
    ICQ = (df_img_sum["ICQ_voxel_sign_final"] / number_pixel) - 0.5
    
    del df_img_masked

    ############################################
    return([pearson, kendall, spearman, M1, M2, ICQ])


