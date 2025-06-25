import os
import pandas as pd
import numpy as np

from articulated_ssm_both_sides.MainASM import run_asm


def test(file_name, demo_factors, marker_radius):
    test_directory = os.path.dirname(__file__)
    data_directory = os.path.join(test_directory, "data")
    marker_data_path = os.path.join(data_directory, file_name)
    # marker_data = pd.read_pickle(marker_data_path)
    marker_data = {}
    with open(marker_data_path, "r") as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) == 4:
                label = parts[0]
                coords = list(map(float, parts[1:]))
                marker_data[label] = coords

    case_name = os.path.splitext(file_name)[0]
    output_directory = os.path.join(test_directory, "_output", case_name)

    run_asm(marker_data, output_directory, demo_factors, marker_radius)


if __name__ == "__main__":
    # test("RCH01.pkl")
    # test("RCH05.pkl")
    # test("S1.pkl")
    # test("S2.pkl")
    test("06_1064.txt", np.array([11, 145, 41, 2, 179.5, 77.4, 71.2, 60.6, 71.5, 58.5]), 0)
    test("10_1347_skin_surface_lms.txt", np.array(
        [9, 135, 38.0, 2, 20.85048010973940, 175.31953869525000, 83.92827146317960, 66.98745752495950,
         58.05935101397360, 67.026293783983, 55.90857549855320]), 0)
    test("13_1096_skin_surface_lms.txt", np.array(
        [5, 104, 16.0, 2, 14.792899408284000, 141.3784538287770, 63.460520074149000, 51.93160518831500,
         38.530202970864400, 52.4974766248662, 44.0693476556198]), 0)
    test("14_3111_skin_surface_lms.txt", np.array(
        [4, 96, 15.0, 1, 16.276041666666700, 136.36277193273000, 66.11512405509830, 41.32046580601270,
         34.91756954728280, 41.42523298567590, 35.55637577818560]), 0)
    test("18_5166_skin_surface_lms.txt", np.array(
        [4, 113, 32.0, 1, 25.060693867961500, 165.11875315548900, 74.67111057593320, 54.020671265506700,
         40.19912132973110, 55.29515837710380, 40.564233474941400]), 0)
    test("2201_skin_surface_lms.txt", np.array(
        [18, 163, 55.0, 1, 20.70081674131510, 160.569752648607, 106.69840074060000, 71.61904098434910,
         56.37639984398010, 73.71260266374000, 57.69812092475080]), 0)
    test("2228_skin_surface_lms.txt", np.array(
        [17, 160, 73.0, 1, 28.515625, 218.0423302748580, 93.55244330743470, 70.16413878202430, 60.45875598313340,
         70.41634690533600, 57.19884630697000]), 0)

'''
Demo factors as array (could be changed to dict):
0: Age, 
1: Height, 
2: Mass, 
3: Sex (1=F, 2=M), 
4: ASIS_width, 
5: PSIS_width, 
6: epicon_width_left, 
7: malleolar_width_left, 
8: epicon_width_right, 
9: malleolar_width_right

Left model uses: Age, Height, Sex, ASIS_width, PSIS_width, left_epicon_width, left_malleolar_width
Right model uses: Age, Height, Sex, ASIS_width, PSIS_width, right_epicon_width
'''
