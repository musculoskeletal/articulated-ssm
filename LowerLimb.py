import LowerLimbSide
import LowerLimbBothSide
import SSMHandler

class LowerLimb:
    def __init__(self, general_fit_settings):
        self.name = general_fit_settings['name']
        self.side = general_fit_settings['side']
        self.include_patella = general_fit_settings['include_patella']
        #self.ssm_handler = ssm_handler

        self.lower_limb_settings = {'dof': {'N_PARAMS_PELVIS': 6,
                                            'N_PARAMS_HIP': 3,
                                            'N_PARAMS_KNEE': 2}, 'directions': {'left': {'hip_flex_coeff': 1.0,
                                                                                         'hip_add_coeff': -1.0,
                                                                                         'hip_rot_coeff': -1.0,
                                                                                         'knee_flex_coeff': -1.0,
                                                                                         'knee_add_coeff': -1.0},
                                                                                'right': {'hip_flex_coeff': 1.0,
                                                                                          'hip_add_coeff': 1.0,
                                                                                          'hip_rot_coeff': 1.0,
                                                                                          'knee_flex_coeff': -1.0,
                                                                                          'knee_add_coeff': 1.0}}}

        if self.side == 'both':
            ssm_handler_l = SSMHandler.SSMHandler(general_fit_settings, 0, side = 'left')
            ssm_handler_r = SSMHandler.SSMHandler(general_fit_settings, 0, side='right')
            self.ll_l = LowerLimbSide.LowerLimbSide('left', ssm_handler_l, general_fit_settings, self.lower_limb_settings)
            self.ll_r = LowerLimbSide.LowerLimbSide('right', ssm_handler_r, general_fit_settings, self.lower_limb_settings)

            #ssm_handler_l = SSMHandler.SSMHandler(general_fit_settings, 0, side = 'left')
            #self.ll_l = LowerLimbSide.LowerLimbSide('left', ssm_handler_l, general_fit_settings, self.lower_limb_settings)
            #ssm_handler_r = SSMHandler.SSMHandler(general_fit_settings, 0, side='right')
            #self.ll_r = LowerLimbSide.LowerLimbSide('right', ssm_handler_r, general_fit_settings, self.lower_limb_settings)
            #self.ll_l.import_opposite_side(self.ll_r)
            #self.ll_r.import_opposite_side(self.ll_l)
        if self.side == 'left':
            ssm_handler_l = SSMHandler.SSMHandler(general_fit_settings, 0, side='left')
            self.ll_l = LowerLimbSide.LowerLimbSide('left', ssm_handler_l, general_fit_settings, self.lower_limb_settings)
        if self.side == 'right':
            ssm_handler_r = SSMHandler.SSMHandler(general_fit_settings, 0, side='right')
            self.ll_r = LowerLimbSide.LowerLimbSide('right',
                                                    ssm_handler_r,
                                                    general_fit_settings,
                                                    self.lower_limb_settings)

