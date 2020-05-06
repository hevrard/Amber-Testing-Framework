# -----------------------------------------------------------------------
# amber_results_comparator.py
# Author: Hari Raval
# -----------------------------------------------------------------------

import csv
import sys
from datetime import date
from datetime import datetime


# compare the csv results from csv1 and csv2; their contents are stored in data1 and data2, respectively
def compare_results(data1, data2, csv1, csv2):
    different_results = []
    csv1_pass_csv2_fail_results = []
    csv2_pass_csv1_fail_results = []
    same_failure_results = []

    # iterate over the data from csv1 and compare it the corresponding data from csv2, saving test cases that
    # match the cases of interest
    for row_index, row in enumerate(data1[1:-1]):
        for col_index, csv1_result in enumerate(row[1:-1]):
            test_type = data1[0][col_index + 1]
            test_number = data1[row_index + 1][0]
            csv2_result = data2[row_index + 1][col_index + 1]
            diff_test = "Test Case: " + test_number + " (" + test_type + ")"
            if csv1_result != csv2_result:
                different_results.append(diff_test)
            if csv1_result == "P" and csv2_result == "F":
                csv1_pass_csv2_fail_results.append(diff_test)
            if csv2_result == "P" and csv1_result == "F":
                csv2_pass_csv1_fail_results.append(diff_test)
            if csv1_result == "F" and csv2_result == "F":
                same_failure_results.append(diff_test)

    # output an error if the total number of tests that differ does not equal the individual sets that one csv passes
    # and the other fails and vice versa
    if len(different_results) != (len(csv1_pass_csv2_fail_results) + len(csv2_pass_csv1_fail_results)):
        print("An error occured during analyzing the table results in counting the number of tests that passed and "
              "failed", file=sys.stderr)
        exit(1)

    # prepare the results of the comparison for output to the .txt file
    final_results = [different_results, csv1_pass_csv2_fail_results, csv2_pass_csv1_fail_results, same_failure_results]
    final_headers = ["Tests that differ between " + str(csv1) + " and " + str(csv2),
                     "Tests that " + str(csv1) + " passes and " + str(csv2) + " fails",
                     "Tests that " + str(csv1) + " fails and " + str(csv2) + " passes",
                     "Tests that both " + str(csv1) + " and " + str(csv2) + " fail"]

    write_results(final_results, final_headers)


# output the formatted statistics between the two csvs in a .txt file named according to the data
def write_results(final_results, final_headers):
    today = date.today()
    todaydate = today.strftime("%Y-%m-%d")
    output_name_txt = "amber_results_comparator_results_" + todaydate + ".txt"
    output_file_txt = open(output_name_txt, "w+")

    for index, each_case in enumerate(final_results):
        output_file_txt.write("-------------------------------------------\n")
        output_file_txt.write(final_headers[index] + "\n")
        output_file_txt.write("-------------------------------------------\n")
        if len(each_case) == 0:
            output_file_txt.write("   NONE")
        for result in each_case:
            output_file_txt.write("   -- " + result)
            output_file_txt.write("\n")
        output_file_txt.write("\n")

    output_file_txt.write("\n")

    output_file_txt.close()


def main():
    if len(sys.argv) != 3:
        print("Please provide two csv files with tables of results generated from amber_test_driver to compare",
              file=sys.stderr)
        exit(1)

    csv1 = sys.argv[1]
    csv2 = sys.argv[2]

    with open(csv1, 'r') as csvfile1, open(csv2, 'r') as csvfile2:
        reader_1 = csv.reader(csvfile1)
        reader_2 = csv.reader(csvfile2)
        data1 = list(reader_1)
        data2 = list(reader_2)

    csv1_headers = " ".join(data1[0])
    csv2_headers = " ".join(data2[0])

    # output an error in the case that the two CSVs differ in dimension, either in their headers or number of rows
    #if csv1_headers != csv2_headers:
     #   print("The two CSVs provided differ in their headers and cannot be properly compared", file=sys.stderr)
      #  exit(1)

    if len(data1) != len(data2):
        print("The two CSVs provided have a different number of rows and cannot be properly compared", file=sys.stderr)
        exit(1)

    compare_results(data1, data2, csv1, csv2)


if __name__ == "__main__":
    main()
