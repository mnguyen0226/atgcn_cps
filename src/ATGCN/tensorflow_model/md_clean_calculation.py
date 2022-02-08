# Scripts takes in the labels and prediction dataset to calculate the mahalanobis distance
# Test calculate the first 10 rows
# Test calculate the first 20 rows
# Calculate and return if there is any negative numbers
# Concatenate the poison datasets in to this, the calibrate to outlier all the poison data points
# Calculate the mean distance of the poison dataset
# Check the math for robust mahalanobis distance


import numpy as np
from pandas import cut
from scipy.stats import chi2
import csv
import matplotlib.pyplot as plt
import seaborn as sns
import scipy as sp
from sklearn.covariance import MinCovDet

EVAL_CLEAN_LABEL_DIR = "out/tgcn/tgcn_scada_wds_lr0.005_batch128_unit64_seq8_pre1_epoch101/eval_clean/eval_clean_labels.csv"
EVAL_CLEAN_PREDS_DIR = "out/tgcn/tgcn_scada_wds_lr0.005_batch128_unit64_seq8_pre1_epoch101/eval_clean/eval_clean_output.csv"
### Poisoned Dataset
# L = 30 #25
# UPPER_TH = 40.5

L = 30 #25
UPPER_TH = 40.5
LOWER_TH = 16
GLOBAL_MEAN_ERROR = np.array(  # Recall calculate everytime retrained model
    # [
    #     0.470392,
    #     0.46830426,
    #     1.33373831,
    #     0.79339774,
    #     1.50138811,
    #     0.42727061,
    #     -0.09867107,
    #     1.13456807,
    #     -1.11697018,
    #     0.3630304,
    #     -1.00766091,
    #     0.62395863,
    #     -0.27923139,
    #     -0.50331974,
    #     -1.27372116,
    #     0.72420398,
    #     -0.25789348,
    #     0.85660608,
    #     0.15255812,
    #     0.21225869,
    #     -0.98057355,
    #     0.8983543,
    #     0.89394346,
    #     0.6814819,
    #     0.13756092,
    #     1.47610716,
    #     0.54627279,
    #     1.62522872,
    #     -0.87679475,
    #     0.47024836,
    #     2.40034568,
    # ]
    [
        0.52865503,
        0.45958133,
        1.25685963,
        0.77171607,
        1.48401157,
        0.47557998,
        -0.10165968,
        1.2389529,
        -2.20679925,
        0.3992842,
        -1.20916699,
        0.59666763,
        -0.30926249,
        -0.48957757,
        -1.22333392,
        0.78566197,
        -0.17307536,
        0.88205641,
        0.08203033,
        0.32419844,
        -1.13448625,
        0.99462164,
        0.7230496,
        0.73255892,
        0.2656382,
        1.4046767,
        0.48527626,
        1.5610318,
        -0.81215967,
        0.46683175,
        2.43063466,
    ]
)

##########
def data_preprocessing(
    num_line=9, label_dataset=EVAL_CLEAN_LABEL_DIR, preds_dataset=EVAL_CLEAN_PREDS_DIR
):
    """Takes in the test_labels.csv, and test_output.csv, converts values from string to float and return the two arrays

    Args:
        num_line (int, optional): Number of array. Defaults to 9.

    Returns:
        Two arrays
    """
    df_eval_labels = []
    df_eval_preds = []

    # Read in the eval ground truth
    with open(label_dataset) as label_file:

        # Read the csv file
        csv_file = csv.reader(label_file)

        # Print the first 10 lines of the csv file
        for i, line in enumerate(csv_file):
            df_eval_labels.append(line)
            if i >= num_line:
                break
    # Close ground truth file
    label_file.close()

    # Read in the eval prediction
    with open(preds_dataset) as pred_file:

        # Read tge csv file
        csv_file = csv.reader(pred_file)

        # Print the first 10 lines of the csv file
        for i, line in enumerate(csv_file):
            df_eval_preds.append(line)
            if i >= num_line:
                break
    # Close prediction file
    pred_file.close()

    # Converts variable from string to float
    for i in range(len(df_eval_labels)):
        df_eval_labels[i] = [float(x) for x in df_eval_labels[i]]
    for i in range(len(df_eval_preds)):
        df_eval_preds[i] = [float(x) for x in df_eval_preds[i]]

    return df_eval_labels, df_eval_preds


##########
def calculate_md_clean():
    """Calculates the Mahalanobis Distance clean dataset"""
    # Get lists
    df_eval_labels, df_eval_preds = data_preprocessing(num_line=1744)

    # Convert lists to numpy arrays
    df_eval_labels = np.array(df_eval_labels)
    df_eval_preds = np.array(df_eval_preds)

    # Get error array between all labels and all predictions
    df_error = df_eval_labels - df_eval_preds

    # 1. Calculate the covariance matrix
    cov = np.cov(df_error, rowvar=False)

    # 2. Calculate cov^-1
    covariance_pm1 = np.linalg.matrix_power(cov, -1)

    # 3. Calculate the global mean error arrayy
    global_mean_error = np.mean(df_error, axis=0)

    # Save the global mean error
    f = open(
        "out/tgcn/tgcn_scada_wds_lr0.005_batch128_unit64_seq8_pre1_epoch101/eval_clean/global_mean_error_clean.txt",
        "w",
    )
    f.write(np.array2string(global_mean_error, separator=","))
    f.close()

    # 4. Calculate the mahalanobis distance
    distances = []
    for i, val in enumerate(df_error):
        p1 = val
        p2 = global_mean_error
        distance = (
            (p1 - p2).T.dot(covariance_pm1).dot(p1 - p2)
        )  # squared mahalanobis distance
        distances.append(distance)
        # print(f"Distance: {distance}")
    distances = np.array(distances)  # 1744 values

    cutoff_arr = []

    for i in range(L, (len(distances))):
        batch_squared_md = distances[i - L : i]  # take the first L batches
        mean_batch_squared_md = np.average(batch_squared_md)
        # batch_cutoff = chi2.pff(0.95, 31)
        cutoff_arr.append(mean_batch_squared_md)
    print(len(cutoff_arr))
    print(f"The Average Mean Squared Mahalanobis Distance {np.average(cutoff_arr)}")

    threshold_line_clean = [UPPER_TH for x in range(len(cutoff_arr))]

    plt.plot(cutoff_arr, label="mean batch squared md")
    plt.plot(threshold_line_clean, label="attacks threshold")
    plt.title(
        "Mean Squared Mahalanobis Distance Every L Hours TimeStamp - Clean Dataset"
    )
    plt.xlabel("Every L hours")
    plt.ylabel("Mean Squared Mahalanobis Distance - To Calibrate Max Threshold")
    plt.show()

    # # Check if there is any negative number in the mahalanobis distance
    # nega = [distances[i] for i in range(len(distances)) if distances[i] <= 0.0]
    # print(f"\nList of negative Mahalanobis Distance: {nega}")

    # # Calculate the average Mahalanobis Distance (not useful)
    # avg_md = np.average(distances)

    # print(f"\nThe average of the Mahalanobis Distance: {avg_md}")

    # # 5. Find the cut-off Chi-Square values. The points outside of 0.95 will be considered as outliers
    # # Note, we also set the degree of freedom values for Chi-Square. This number is equal to the number of variables in our dataset, 31
    # cutoff = chi2.ppf(
    #     0.99999999999999999, df_error.shape[1]
    # )  # THRESHOLD = 0.99999999999999999

    # # Index of outliers
    # outlier_index = np.where(distances > cutoff)

    # print("\nTIME SERIES INDEX OF OUTLIERS:")
    # print(outlier_index)

    # # print("OUTLIERS DETAILS\n")
    # # print(df_error[ distances > cutoff , :])


##########
def calculate_rmd_clean():
    """Calculates Robust Mahalanobus Distance clean dataset"""
    df_eval_labels, df_eval_preds = data_preprocessing(num_line=1744)

    # Convert lists to numpy arrays
    df_eval_labels = np.array(df_eval_labels)
    df_eval_preds = np.array(df_eval_preds)

    # Get error array between all labels and all predictions
    df_error = df_eval_labels - df_eval_preds

    # 1. Calculate Minimum Covariance Determinant
    rng = np.random.RandomState(0)

    # 2. Calculate the covariance matrix
    real_cov = np.cov(df_error, rowvar=False)

    # 3. Get multivariate values
    X = rng.multivariate_normal(mean=np.mean(df_error, axis=0), cov=real_cov, size=506)

    # 4. Get MCD values
    cov = MinCovDet(random_state=0).fit(X)
    mcd = cov.covariance_  # robust covariance metrics

    # 5. Calculate the global mean error
    global_mean_error = cov.location_

    # Save the global mean error
    f = open(
        "out/tgcn/tgcn_scada_wds_lr0.005_batch128_unit64_seq8_pre1_epoch101/eval_clean/global_mean_error_clean.txt",
        "a",
    )
    f.write("\n\n")
    f.write(np.array2string(global_mean_error, separator=","))
    f.close()

    # 6. Calculate the invert covariance matrix
    inv_covmat = sp.linalg.inv(mcd)

    # 4. Calculate the mahalanobis distance
    distances = []
    for i, val in enumerate(df_error):
        p1 = val
        p2 = global_mean_error
        distance = (
            (p1 - p2).T.dot(inv_covmat).dot(p1 - p2)
        )  # squared mahalanobis distance
        distances.append(distance)
        # print(f"Distance: {distance}")
    distances = np.array(distances)  # 1744 values

    cutoff_arr = []

    for i in range(L, (len(distances))):
        batch_squared_md = distances[i - L : i]  # take the first L batches
        mean_batch_squared_md = np.average(batch_squared_md)
        # batch_cutoff = chi2.pff(0.95, 31)
        cutoff_arr.append(mean_batch_squared_md)
    print(len(cutoff_arr))
    print(f"The Average Mean Squared Mahalanobis Distance {np.average(cutoff_arr)}")

    threshold_line_clean = [UPPER_TH for x in range(len(cutoff_arr))]

    plt.plot(cutoff_arr, label="mean batch squared md")
    plt.plot(threshold_line_clean, label="attacks threshold")
    plt.title(
        "Mean Squared Mahalanobis Distance Every L Hours TimeStamp - Clean Dataset"
    )
    plt.xlabel("Every L hours")
    plt.ylabel("Mean Squared Mahalanobis Distance - To Calibrate Max Threshold")
    plt.show()


if __name__ == "__main__":
    calculate_md_clean()
    calculate_rmd_clean()
