import numpy as np
from copy import deepcopy
from gias3.common import math
from gias3.visualisation import fieldvi

CORRECT_FOR_SKIN_PADDING_AND_MARKER_RADIUS = False
SKIN_PADDING = 5
MARKER_RADIUS = 5


def correct_target_markers(target_markers_per_bone, side_m):
    """Correct the target marker location using the marker radius and skin padding
    target_markers_per_bone [dict]: Dictionary with the bones, marker_names and coordinates of each target marker per
                                    side:
                                    target_markers_per_bone = {bone: {'left': {markername1: xyz,
                                                                               markername2: xyz},
                                                                      'right': {markername1: xyz,
                                                                                markername2: xyz}}}
    plot [boolean]: True = plot results, False = do not plot results
    """

    original_target_markers_per_bone = deepcopy(target_markers_per_bone)

    oa = (np.asarray(target_markers_per_bone['left']['ASIS']) +
          np.asarray(target_markers_per_bone['right']['ASIS'])) / 2
    op = (np.asarray(target_markers_per_bone['left']['PSIS']) +
          np.asarray(target_markers_per_bone['right']['PSIS'])) / 2

    ap_axis = math.norm(op - oa)

    if side_m == 'left':
        ml_axis_fem = math.norm(np.asarray(target_markers_per_bone['left']['LEC']) -
                                np.asarray(target_markers_per_bone['left']['MEC']))
        ml_axis_tib = math.norm(np.asarray(target_markers_per_bone['left']['malleolus_lat']) -
                                np.asarray(target_markers_per_bone['left']['malleolus_med']))
        for side in target_markers_per_bone.keys():
            for lm_name in target_markers_per_bone[side].keys():
                if lm_name == 'ASIS':  # Move marker location posteriorly
                    target_markers_per_bone[side][lm_name] = \
                        target_markers_per_bone[side][lm_name] + \
                        ap_axis * (MARKER_RADIUS + SKIN_PADDING)
                elif lm_name == 'PSIS' or lm_name == 'SAC':  # Move marker location anteriorly
                    target_markers_per_bone[side][lm_name] = \
                        target_markers_per_bone[side][lm_name] - \
                        ap_axis * (MARKER_RADIUS + SKIN_PADDING)
                elif lm_name == 'MEC':  # Move marker location laterally
                    target_markers_per_bone[side][lm_name] = \
                        target_markers_per_bone[side][lm_name] + \
                        ml_axis_fem * (MARKER_RADIUS + SKIN_PADDING)
                elif lm_name == 'LEC':  # Move marker location medially
                    target_markers_per_bone[side][lm_name] = \
                        target_markers_per_bone[side][lm_name] - \
                        ml_axis_fem * (MARKER_RADIUS + SKIN_PADDING)
                elif lm_name == 'malleolus_med':  # Move marker location laterally
                    target_markers_per_bone[side][lm_name] = \
                        target_markers_per_bone[side][lm_name] + \
                        ml_axis_tib * (MARKER_RADIUS + SKIN_PADDING)
                elif lm_name == 'malleolus_lat':  # Move marker location medially
                    target_markers_per_bone[side][lm_name] = \
                        target_markers_per_bone[side][lm_name] - \
                        ml_axis_tib * (MARKER_RADIUS + SKIN_PADDING)
                else:
                    print(lm_name)
                    print('Error in skin padding and marker radius correction')
                    input()

    elif side_m == 'right':
        ml_axis_fem = math.norm(np.asarray(target_markers_per_bone['right']['LEC']) -
                                np.asarray(target_markers_per_bone['right']['MEC']))
        ml_axis_tib = math.norm(np.asarray(target_markers_per_bone['right']['malleolus_lat']) -
                                np.asarray(target_markers_per_bone['right']['malleolus_med']))
        for side in target_markers_per_bone.keys():
            for lm_name in target_markers_per_bone[side]:
                if lm_name == 'ASIS':  # Move marker location posteriorly
                    target_markers_per_bone[side][lm_name] = \
                        target_markers_per_bone[side][lm_name] + \
                        ap_axis * (MARKER_RADIUS + SKIN_PADDING)
                elif lm_name == 'PSIS' or lm_name == 'SAC':  # Move marker location anteriorly
                    target_markers_per_bone[side][lm_name] = \
                        target_markers_per_bone[side][lm_name] - \
                        ap_axis * (MARKER_RADIUS + SKIN_PADDING)
                elif lm_name == 'MEC':  # Move marker location laterally
                    target_markers_per_bone[side][lm_name] = \
                        target_markers_per_bone[side][lm_name] + \
                        ml_axis_fem * (MARKER_RADIUS + SKIN_PADDING)
                elif lm_name == 'LEC':  # Move marker location medially
                    target_markers_per_bone[side][lm_name] = \
                        target_markers_per_bone[side][lm_name] - \
                        ml_axis_fem * (MARKER_RADIUS + SKIN_PADDING)
                elif lm_name == 'malleolus_med':  # Move marker location laterally
                    target_markers_per_bone[side][lm_name] = \
                        target_markers_per_bone[side][lm_name] + \
                        ml_axis_tib * (MARKER_RADIUS + SKIN_PADDING)
                elif lm_name == 'malleolus_lat':  # Move marker location medially
                    target_markers_per_bone[side][lm_name] = \
                        target_markers_per_bone[side][lm_name] - \
                        ml_axis_tib * (MARKER_RADIUS + SKIN_PADDING)
                else:
                    print('Error in skin padding and marker radius correction')

    else:
        for side in target_markers_per_bone.keys():
            ml_axis_fem = math.norm(np.asarray(target_markers_per_bone[side]['LEC']) -
                                    np.asarray(target_markers_per_bone[side]['MEC']))
            ml_axis_tib = math.norm(np.asarray(target_markers_per_bone[side]['malleolus_lat']) -
                                    np.asarray(target_markers_per_bone[side]['malleolus_med']))
            for lm_name in target_markers_per_bone[side]:
                if lm_name == 'ASIS':  # Move marker location posteriorly
                    target_markers_per_bone[side][lm_name] = \
                        target_markers_per_bone[side][lm_name] + \
                        ap_axis * (MARKER_RADIUS + SKIN_PADDING)
                elif lm_name == 'PSIS' or lm_name == 'SAC':  # Move marker location anteriorly
                    target_markers_per_bone[side][lm_name] = \
                        target_markers_per_bone[side][lm_name] - \
                        ap_axis * (MARKER_RADIUS + SKIN_PADDING)
                elif lm_name == 'MEC':  # Move marker location laterally
                    target_markers_per_bone[side][lm_name] = \
                        target_markers_per_bone[side][lm_name] + \
                        ml_axis_fem * (MARKER_RADIUS + SKIN_PADDING)
                elif lm_name == 'LEC':  # Move marker location medially
                    target_markers_per_bone[side][lm_name] = \
                        target_markers_per_bone[side][lm_name] - \
                        ml_axis_fem * (MARKER_RADIUS + SKIN_PADDING)
                elif lm_name == 'malleolus_med':  # Move marker location laterally
                    target_markers_per_bone[side][lm_name] = \
                        target_markers_per_bone[side][lm_name] + \
                        ml_axis_tib * (MARKER_RADIUS + SKIN_PADDING)
                elif lm_name == 'malleolus_lat':  # Move marker location medially
                    target_markers_per_bone[side][lm_name] = \
                        target_markers_per_bone[side][lm_name] - \
                        ml_axis_tib * (MARKER_RADIUS + SKIN_PADDING)
                else:
                    print('Error in skin padding and marker radius correction')
    #if plot:
     #   v = fieldvi.FieldVi()
      #  lms = []
       # lms_original = []
        #for bone in target_markers_per_bone.keys():
         #   for side in target_markers_per_bone[bone].keys():
          #      for lm in target_markers_per_bone[bone][side].keys():
           #         lms.append(target_markers_per_bone[bone][side][lm])
            #        lms_original.append(original_target_markers_per_bone[bone][side][lm])
        #v.addData('target_lms_original',
        #          np.asarray(lms_original),
        #          render_args={'mode': 'sphere', 'scale_factor': 10.0, 'color': (0, 0, 1)})
        #v.addData('target_lms',
        #          np.asarray(lms),
        #          render_args={'mode': 'sphere', 'scale_factor': 10.0, 'color': (0, 1, 0)})
        #v.configure_traits()