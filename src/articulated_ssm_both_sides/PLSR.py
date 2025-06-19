import numpy as np
import os
import pandas as pd
from gias3.learning import PCA
from sklearn.cross_decomposition import PLSRegression
import joblib


def rf_predict(predictors, model, weights):
    '''
    using a sklearn random forest algorithm saved as a pkl file, predict the response from the given model
    '''
    pred = predictors.reshape(1,-1)
    model = joblib.load(model)
    prediction = (model.predict(pred)).squeeze()
    # convert to sd not absolute weight
    init_pc_weights = np.zeros(len(prediction))
    for j in range(len(prediction)):
        init_pc_weights[j] = prediction[j] / np.sqrt(weights[j])
    print(init_pc_weights)
    return init_pc_weights

def plsr(case_data, anthro_data, general_fit_settings):
    """
    Function to run PLSR for a single case. Before running
    create a csv file with all the anthro measurements where rows=case, cols=anthro measurement
    Parameters. Code will create an anthropological measurements file according to the
    bone names which are used in the SSM and put them in the correct order to align
    with the PCAs.
    ----------
    bone : name of the bone e.g. Left_femur
    root_dir : location of shape model folders

    Returns
    -------
    predicted weights and st dev of predicted weights

    Requires a .csv  file with anthropological data, can be in any order.
    First column must have case name which matches the bone stl files.
    If gender is included, this must be in the second column and all other factors
    must be numbers.

    author: Laura Carman

    """
    print("--starting PLSR")
    np.set_printoptions(threshold=np.inf)

    P = pd.read_csv(anthro_data, header=None)
    predictors_train = P.iloc[:, [0, 2, 6, 7, 11]].copy()  # columns of anthro data you want to use for prediction
    predictors_train.drop([0], axis=0, inplace=True)  # remove case name

    ssm_name = general_fit_settings['ssm_name']
    side = general_fit_settings['side']
    ssm_name_bones_incl = 'pel_fem_tib_fib'
    coupled_ssm_dir = r'{}/coupled_ssm/{}_{}_side'.format(os.getcwd(), ssm_name_bones_incl,
                                                          side)  # directory of your ssm
    ssm_pc_file = r'{}/{}.pc.npz'.format(coupled_ssm_dir, ssm_name)
    coupled_pcs = PCA.loadPrincipalComponents(ssm_pc_file)
    # Load files of principal component weightings of the mesh
    Y = coupled_pcs.projectedWeights
    Y = Y.T
    i = 0
    j = 0
    predictors_train.drop([0], axis=1, inplace=True)

    pls2 = PLSRegression(scale=True)
    pls2.fit(predictors_train, Y)  # where Z = training vectors and Y = target vectors
    pred_weights = np.zeros((len(Y) - 1))
    pred_sd = np.zeros((len(Y) - 1))

    # Apply PLSR
    pred_weights = pls2.predict([case_data])[0]
    for j in range(len(pred_weights)):
        pred_sd[j] = np.array(pred_weights[j]) / np.sqrt(coupled_pcs.weights[j])
    # pred_sd_2[:,i] = coupled_pcs.calcSDFromWeights([0], pred_weights[:,i])
    print(pred_sd[:5])
    print(pred_weights[:5])
    # print(pred_sd[:5,i])

    print("--completed PLSR")
    return pred_weights, pred_sd


def plsr_loo(bone_names, anthro_data, ssm_path, general_fit_settings):
    """
    Function to run PLSR for the use in a leave one out analysis. Before running
    create a csv file with all the anthro measurements where rows=case, cols=anthro measurement
    Parameters. Code will create an anthropological measurements file according to the
    bone names which are used in the SSM and put them in the correct order to align
    with the PCAs.
    ----------
    bone : name of the bone e.g. Left_femur
    root_dir : location of shape model folders

    Returns
    -------
    One csv file with all the weights for each bone in the working directory

    Requires a .csv  file with anthropological data, can be in any order.
    First column must have case name which matches the bone stl files.
    If gender is included, this must be in the second column and all other factors
    must be numbers.

    """
    print("--starting PLSR")
    np.set_printoptions(threshold=np.inf)

    P = pd.read_csv(anthro_data, header=None)
    predictors = P.iloc[:, [0, 2, 6, 7, 11]].copy()
    n = len(bone_names)

    validation_path = os.path.join(ssm_path, 'Left_side')
    k = 0
    for case in predictors.iloc[:, 0]:
        if case in bone_names:
            k = k + 1
            continue
        else:
            predictors.drop([predictors.index[k]], axis=0, inplace=True)
            k = k - 1
        k = k + 1
    predictors.drop([0], axis=1, inplace=True)
    i = 0
    pred_weights = np.zeros((130, len(predictors)))
    pred_sd = np.zeros((130, len(predictors)))
    for i in range(len(bone_names)):
        test_case = predictors.iloc[[i]]  # anthro measurements of current bone
        Z = predictors.drop([predictors.index[i]])
        coupled_ssm_dir = os.path.join(validation_path + str(i) + '.pc.npz')
        coupled_pcs = PCA.loadPrincipalComponents(coupled_ssm_dir)
        # Load files of principal component weightings of the mesh
        Y = coupled_pcs.projectedWeights
        Y = Y.T
        pls2 = PLSRegression(scale=True)
        pls2.fit(Z, Y)  # where Z = training vectors and Y = target vectors
        pred_weights[:, i] = pls2.predict(test_case)
        for j in range(len(pred_weights)):
            pred_sd[j, i] = np.array(pred_weights[j, i]) / np.sqrt(coupled_pcs.weights[j])

    print("--completed PLSR")
    return pred_weights, pred_sd


def plsr_train_test(test_set, train_set, anthro_data, general_fit_settings):
    """
    Function to run PLSR for the use in a leave one out analysis. Before running
    create a csv file with all the anthro measurements where rows=case, cols=anthro measurement
    Parameters. Code will create an anthropological measurements file according to the
    bone names which are used in the SSM and put them in the correct order to align
    with the PCAs.
    ----------
    bone : name of the bone e.g. Left_femur
    root_dir : location of shape model folders

    Returns
    -------
    One csv file with all the weights for each bone in the working directory

    Requires a .csv  file with anthropological data, can be in any order.
    First column must have case name which matches the bone stl files.
    If gender is included, this must be in the second column and all other factors
    must be numbers.

    """
    print("--starting PLSR")
    np.set_printoptions(threshold=np.inf)

    P = pd.read_csv(anthro_data, header=None)
    predictors_train = P.iloc[:, [0, 2, 6, 7, 11]].copy()
    predictors_test = predictors_train.copy()

    ssm_name = general_fit_settings['ssm_name']
    side = general_fit_settings['side']
    ssm_name_bones_incl = 'pel_fem_tib_fib'
    coupled_ssm_dir = r'{}/coupled_ssm/{}_{}_side'.format(os.getcwd(), ssm_name_bones_incl, side)
    ssm_pc_file = r'{}/{}.pc.npz'.format(coupled_ssm_dir, ssm_name)
    coupled_pcs = PCA.loadPrincipalComponents(ssm_pc_file)
    # Load files of principal component weightings of the mesh
    Y = coupled_pcs.projectedWeights
    Y = Y.T
    i = 0
    j = 0
    for case in predictors_train.iloc[:, 0]:
        if case in train_set:
            i = i + 1
            continue
        else:
            predictors_train.drop([predictors_train.index[i]], axis=0, inplace=True)
            i = i - 1
        i = i + 1
    predictors_train.drop([0], axis=1, inplace=True)

    for case in predictors_test.iloc[:, 0]:
        if case in test_set:
            j = j + 1
            continue
        else:
            predictors_test.drop([predictors_test.index[j]], axis=0, inplace=True)
            j = j - 1
        j = j + 1
    predictors_test.drop([0], axis=1, inplace=True)

    pls2 = PLSRegression(scale=True)
    pls2.fit(predictors_train, Y)  # where Z = training vectors and Y = target vectors
    pred_weights = np.zeros((len(Y) - 1, len(test_set)))
    pred_sd = np.zeros((len(Y) - 1, len(test_set)))
    pred_sd_2 = np.zeros((len(Y) - 1, len(test_set)))
    for i in range(len(test_set)):
        test_case = predictors_test.iloc[[i]]  # anthro measurements of current bone
        # Apply PLSR
        pred_weights[:, i] = pls2.predict(test_case)
        for j in range(len(pred_weights)):
            pred_sd[j, i] = np.array(pred_weights[j, i]) / np.sqrt(coupled_pcs.weights[j])
        # pred_sd_2[:,i] = coupled_pcs.calcSDFromWeights([0], pred_weights[:,i])
        # print(pred_sd[:5,i])
        # print(pred_weights[:5,i])
        # print(pred_sd[:5,i])

    print("--completed PLSR")
    return pred_weights, pred_sd
