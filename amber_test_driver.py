# -----------------------------------------------------------------------
# amber_test_driver.py
# Author: Hari Raval
# -----------------------------------------------------------------------
import os
import sys


def main():
    if len(sys.argv) != 2:
        print("Please provide a directory of .txt files to parse and process into Amber tests", file=sys.stderr)
        exit(1)

    input_dir = sys.argv[1]

    output_dir = "driver_amber_tests_output/"

    os.system("mkdir " + output_dir)

    for file_name in os.listdir(input_dir):
        if file_name.endswith('.txt'):

            # the input file name should not end with .amber as the amber_test_generation.py script will add the
            # extension upon output
            output_file_name = file_name[:-4] + "_txt"
            generate_test = "python3 amber_test_generation.py " + input_dir + "/" + file_name + " " + output_file_name
            os.system(generate_test)

            output_file_name = output_file_name + ".amber"
            move_amber_test_file = "mv " + output_file_name + " " + output_dir
            os.system(move_amber_test_file)

    for index, file_name in enumerate(os.listdir(output_dir)):
        if file_name.endswith('.amber'):

            run_amber_test = "/localdisk/tsoren99/amber/amber/out/Debug/amber " + output_dir + file_name + \
                             " -d >> temp_results.txt"

            os.system(run_amber_test)
            current_test = "Test: " + str(index)

            with open('temp_results.txt', 'a') as file:
                file.write(current_test)
                file.write("\n")

    # analysis of output file
    output = open("final_results.txt", "a")

    with open('temp_results.txt', 'r') as file:
        results = file.read()

    results_list = results.split('\n')
    while "" in results_list:
        results_list.remove("")

    labeled_results_list = []

    for index, results in enumerate(results_list):

        if index % 2 == 0:
            temp_list = [results_list[index], results_list[index + 1]]
            labeled_results_list.append(temp_list)

    passed_test_count = 0
    failed_test_count = 0

    # format output table to clean it up
    for result in labeled_results_list:
        if "1 pass" in result[0]:
            output.write(result[1] + " | " + "passed")
            passed_test_count = passed_test_count + 1
        elif "1 fail" in result[0]:
            failed_test_count = failed_test_count + 1
            output.write(result[1] + " | " + "passed")

        output.write("\n")

    output.write("\n\n")
    output.write("Total Passed: " + str(passed_test_count) + "\n")
    output.write("Total Failed: " + str(failed_test_count) + "\n")


if __name__ == "__main__":
    main()
