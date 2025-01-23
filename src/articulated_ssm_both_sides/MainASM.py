# Main articulated SSM model fitting script
# 25/01/2023

from LowerLimb import LowerLimb as LowerLimb
import numpy as np
import os
import LandmarkHandler
import SegmentationHandler
import FitASM_2 as FitASM
import time
import PLSR

startTime = time.time()
general_fit_settings = {'segm_fit': False,                           # Fit using segmentation data
                        'lm_fit': True,                            # Fit using landmark coordinates
                        'include_patella': False,                    # Include patella
                        'patella_shift': np.array([50, 50, -10]),
                        'pc_modes': [[0],[0,1,2,3]], #, [[0,1],[0, 1, 2, 3, 4]],      # PC modes to fit (multi fit: [[],[]])
                        'mweight': [1,0.0001], #[1, 0.01],                        # Mahalanobis weight (multi fit: [float, float])
                        'min_args': {'method': 'Powell'},#{'method': 'BFGS','jac': False,'bounds': None, 'tol': 1e-6,'options': {'eps': 1e-5}},
                                    #{'method': 'Powell'},           # scipy.optimize minimisation algorithm
                        'knee_gap': 5,                               # Minimal gap between femur and tibia knee nodes
                        'knee_fixed': False,                          # Fix the knee in initial position (0)
                        'allow_knee_adduction_dof': True,            # Allow rotation in VV when placing tibia-fibula
                        'allow_knee_adduction_correction': True,     # Allow VV rotation to obtain minimal knee gap
                        'pred_path': 'RCH05',
                        'x0': None,                                  # Initial parameters for the 1st fit
                        'init_pc_weights': None,                      # Initial weights for each mode in the first fit.
                        'correct_markers': True,                     # if motion capture markers are used for prediction: True
                        'PLSR': False,                                  # if a partial least squares regression is being conducted to provide an initial guess to the shape model
                        'case_name': 'RCH05'
                        }

# load the coupled SSM
#ssm_handler = SSMHandler.SSMHandler(general_fit_settings, 0)
anthro_data_path = r'{}/target_landmarks/Left_side_all_predictive_factors.csv'.format(os.getcwd())
pred_path = '{}/pred_meshes/{}'.format(os.getcwd(),general_fit_settings['pred_path'])
if not os.path.exists(pred_path):
    os.makedirs(pred_path)
errors_path = '{}/pred_meshes/{}/shape_model_lm_errors.txt'.format(os.getcwd(),general_fit_settings['pred_path'])
case_data = np.array([133,313.6,159.4,297.2]) #height,ASIS width,fem length,tib length
if os.path.exists(errors_path):
    os.remove(errors_path)
errors = open(errors_path, 'w+')
errors.write('mae_lm,rmse_lm,mweight\n')
# Generate lower limb model
test_model = LowerLimb(general_fit_settings)

if general_fit_settings['PLSR'] == True:
    pred_weights, pred_sd = PLSR.plsr(case_data, anthro_data_path, general_fit_settings)
    if isinstance(general_fit_settings['pc_modes'][0], (list, tuple, np.ndarray)):
        general_fit_settings['init_pc_weights'] = pred_sd[:(len(general_fit_settings['pc_modes'][-1]))]
    else:
        general_fit_settings['init_pc_weights'] = pred_sd[:(len(general_fit_settings['pc_modes']))]
        print(general_fit_settings['init_pc_weights'])

# Load bones and model.
test_model.ll_l.load_bones_and_model()
test_model.ll_r.load_bones_and_model()

# Initialize data for minimisation
fit_data = {}  # Dictionary with data to fit the ASM to

# load segmentation data to fit to
if general_fit_settings['segm_fit']:
    segmentations_dir = r'{}/segmentations'.format(os.getcwd())
    segmentation_handler = SegmentationHandler.SegmentationHandler(segmentations_dir, general_fit_settings)
    fit_data['segmentation_handler'] = segmentation_handler

# load landmark coordinates data to fit to
if general_fit_settings['lm_fit']:
    target_lms_file = r'{}/target_landmarks/{}_landmarks_mocap.txt'.format(os.getcwd(), general_fit_settings['case_name'])
    landmark_names_to_fit = ['ASIS', 'PSIS', 'SAC', 'LEC', 'MEC', 'malleolus_med', 'malleolus_lat']
    landmark_handler_l = LandmarkHandler.LandmarkHandler(target_lms_file, landmark_names_to_fit, test_model, general_fit_settings['correct_markers'], 'left')
    fit_data['landmark_handler_l'] = landmark_handler_l
    landmark_handler_r = LandmarkHandler.LandmarkHandler(target_lms_file, landmark_names_to_fit, test_model,
                                                         general_fit_settings['correct_markers'], 'right')
    fit_data['landmark_handler_r'] = landmark_handler_r

# Fit articulated SSM
asm_fitter_l = FitASM.FitASM(test_model, general_fit_settings, fit_data, general_fit_settings['case_name'], 'left')
errors.write(str(asm_fitter_l.mae_lm)+','+str(asm_fitter_l.rmse_lm)+','+str(asm_fitter_l.opt_mweight)+'\n')
exectutionTime = (time.time() - startTime)
print('Execution time in seconds: ' + str(exectutionTime))

asm_fitter_r = FitASM.FitASM(test_model, general_fit_settings, fit_data, general_fit_settings['case_name'], 'right')
errors.write(str(asm_fitter_r.mae_lm)+','+str(asm_fitter_r.rmse_lm)+','+str(asm_fitter_r.opt_mweight)+'\n')
exectutionTime = (time.time() - startTime)
print('Execution time in seconds: ' + str(exectutionTime))