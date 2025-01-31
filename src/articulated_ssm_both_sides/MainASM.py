# Main articulated SSM model fitting script
# 25/01/2023

import os
import numpy as np

from articulated_ssm_both_sides.FitASM_2 import FitASM
from articulated_ssm_both_sides.LandmarkHandler import LandmarkHandler
from articulated_ssm_both_sides.SegmentationHandler import SegmentationHandler
from articulated_ssm_both_sides.LowerLimb import LowerLimb
from articulated_ssm_both_sides.PLSR import plsr


general_fit_settings = {
    'segm_fit': False,                          # Fit using segmentation data
    'lm_fit': True,                             # Fit using landmark coordinates
    'include_patella': False,                   # Include patella
    'patella_shift': np.array([50, 50, -10]),
    'pc_modes': [[0], [0, 1, 2, 3]],            # , [[0,1],[0, 1, 2, 3, 4]],    # PC modes to fit (multi fit: [[],[]])
    'mweight': [1, 0.0001],                     # [1, 0.01],                    # Mahalanobis weight (multi fit: [float, float])
    'min_args': {'method': 'Powell'},           # {'method': 'BFGS','jac': False,'bounds': None, 'tol': 1e-6,'options': {'eps': 1e-5}},
    'knee_gap': 5,                              # Minimal gap between femur and tibia knee nodes
    'knee_fixed': False,                        # Fix the knee in initial position (0)
    'allow_knee_adduction_dof': True,           # Allow rotation in VV when placing tibia-fibula
    'allow_knee_adduction_correction': True,    # Allow VV rotation to obtain minimal knee gap
    'pred_path': 'RCH05',
    'x0': None,                                 # Initial parameters for the 1st fit
    'init_pc_weights': None,                    # Initial weights for each mode in the first fit.
    'correct_markers': True,                    # if motion capture markers are used for prediction: True
    'PLSR': False,                              # if a partial least squares regression is used to provide an initial guess to shape model
    'case_name': 'RCH05'
    }


def run_asm(marker_data):

    # Load the coupled SSM.
    pred_path = '{}/pred_meshes/{}'.format(os.getcwd(), general_fit_settings['pred_path'])
    if not os.path.exists(pred_path):
        os.makedirs(pred_path)
    errors_path = '{}/pred_meshes/{}/shape_model_lm_errors.txt'.format(os.getcwd(), general_fit_settings['pred_path'])

    if os.path.exists(errors_path):
        os.remove(errors_path)
    errors = open(errors_path, 'w+')
    errors.write('mae_lm,rmse_lm,mweight\n')

    # Generate and load lower limb model.
    lower_limb_model = LowerLimb(general_fit_settings)
    lower_limb_model.ll_l.load_bones_and_model()
    lower_limb_model.ll_r.load_bones_and_model()

    # Load landmark coordinates data to fit to.
    fit_data = landmark_fit(lower_limb_model, marker_data)

    # Fit articulated SSM
    asm_fitter_l = FitASM(lower_limb_model, general_fit_settings, fit_data, general_fit_settings['case_name'], 'left')
    errors.write(str(asm_fitter_l.mae_lm)+','+str(asm_fitter_l.rmse_lm)+','+str(asm_fitter_l.opt_mweight)+'\n')
    asm_fitter_r = FitASM(lower_limb_model, general_fit_settings, fit_data, general_fit_settings['case_name'], 'right')
    errors.write(str(asm_fitter_r.mae_lm)+','+str(asm_fitter_r.rmse_lm)+','+str(asm_fitter_r.opt_mweight)+'\n')


def landmark_fit(lower_limb_model, marker_data):
    landmark_names_to_fit = ['ASIS', 'PSIS', 'SAC', 'LEC', 'MEC', 'malleolus_med', 'malleolus_lat']

    fit_data = {}
    for side in ['left', 'right']:
        fit_data[f'landmark_handler_{side[0]}'] = LandmarkHandler(
            marker_data, landmark_names_to_fit, lower_limb_model, general_fit_settings['correct_markers'], side
        )

    return fit_data


def segmentation_fit():
    segmentations_dir = r'{}/segmentations'.format(os.getcwd())
    segmentation_handler = SegmentationHandler(segmentations_dir, general_fit_settings)
    fit_data = {'segmentation_handler': segmentation_handler}

    return fit_data


def plsr_fit():
    anthro_data_path = r'{}/target_landmarks/Left_side_all_predictive_factors.csv'.format(os.getcwd())
    case_data = np.array([133, 313.6, 159.4, 297.2])  # height,ASIS width,fem length,tib length
    pred_weights, pred_sd = plsr(case_data, anthro_data_path, general_fit_settings)
    if isinstance(general_fit_settings['pc_modes'][0], (list, tuple, np.ndarray)):
        general_fit_settings['init_pc_weights'] = pred_sd[:(len(general_fit_settings['pc_modes'][-1]))]
    else:
        general_fit_settings['init_pc_weights'] = pred_sd[:(len(general_fit_settings['pc_modes']))]
        print(general_fit_settings['init_pc_weights'])
