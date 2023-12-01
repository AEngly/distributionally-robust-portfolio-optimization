import os
import numpy as np

def find_latest_id(file_name, folder_path, expId=2):

    # List all files in the folder
    files = os.listdir(folder_path)

    # Filter files that match the "id_X_" pattern
    id_files = [file for file in files if file.startswith("id") and file_name in file and "Experiment{}".format(expId) in file]

    # If there are no existing files, start with ID 1
    if not id_files:
        return 1

    # Extract the IDs and find the maximum
    ids = [int(file[2]) for file in id_files]
    latest_id = max(ids)

    # Increment the latest ID for the new experiment
    return latest_id + 1

def write_parameters_to_file(data, parameters, file_name="ExcessModelDRO", folder_path="./Results/Chapter5_ExcessCVaR/", expId=2):

    # Get the right id
    id = find_latest_id(file_name, folder_path, expId=expId)

    # Specify paths
    log_path = folder_path + "ExperimentLog.txt"
    file_path = folder_path + "id{}".format(id) + "_" + file_name + "_" + "Experiment{}".format(expId) + ".csv"

    # Then we save the experiment data
    np.savetxt(file_path, data, fmt='%.18e', delimiter=' ')

    # Write the parameters to the file
    with open(log_path, 'a') as file:
        file.write(f"------- (id, experiment): ({id}, {expId}) ------- \n{parameters}\n\n")