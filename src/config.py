from pathlib import Path

data_dir = (Path().cwd().parents[0] / 'data').absolute()
data_raw = data_dir / 'raw'
data_mask = data_dir / 'masks'
data_cells = data_dir / 'cells'
data_cp = data_dir / 'cell_profiler' / 'result'
data_figure = (Path().cwd().parents[0] / 'figures').absolute()

dataset_BM = "BM_bgsub"
dataset_UC = "UC_bgsub"

data_path_BM = f"{data_raw}/{dataset_BM}/"
data_path_mask_BM = f"{data_mask}/{dataset_BM}/"
data_path_masked_BM = f"{data_cells}/{dataset_BM}/"

data_path_UC = f"{data_raw}/{dataset_UC}/"
data_path_mask_UC = f"{data_mask}/{dataset_UC}/"
data_path_masked_UC = f"{data_cells}/{dataset_UC}/"

channel_names = ["ATF6", "BetaTubulin", "ConcanavalinA", "DAPI", "GOLPH4", "HSP60", "Nucleolin", "Phalloidin", "Sortilin", "TOM20", "WGA"]
idx_channel_names = [channel_names.index(chan) for chan in channel_names]

channel_names_modif = ['ATF6', 'DAPI', 'GOLPH4', 'Nucleolin', 'TOM20']
idx_channel_names_modif = [channel_names.index(chan_modif) for chan_modif in channel_names_modif]

dict_marker_organelle = {
    'TOM20':'mitochondria',
    'HSP60':'mitochondria',
    'ATF6':'endoplasmic_reticulum',
    'ConcanavalinA':'endoplasmic_reticulum',
    'Nucleolin':'nucleus',
    'DAPI':'nucleus',
    'Phalloidin':'actin_filaments',
    'BetaTubulin':'microtubules',
    'GOLPH4':'golgi',
    'WGA':'golgi',
    'Sortilin':'golgi'
}

BM_indices = [2, 3, 8, 14, 18, 29, 30]
UC_indices = [0, 3, 9, 11, 19, 23, 30]