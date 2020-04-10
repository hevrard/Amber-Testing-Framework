# -----------------------------------------------------------------------
# amber_test_driver.py
# Author: Hari Raval
# -----------------------------------------------------------------------
import os
import sys
import csv
import socket # to get hostname
from configuration import Configuration
import amber_test_generation
from tabulate import tabulate
from datetime import date
from datetime import datetime
import time

AMBER_PATHS=["amber",
                   "/localdisk/tsoren99/amber/amber/out/Debug/amber",
                   "/home/tyler/Documents/amber/amber/out/Debug/amber"]

LOG_FILE = None

def log_print(s):
    global LOG_FILE
    LOG_FILE.write(s + "\n")
    print(s)


# create amber tests with provided input directory and specified configuration object and path/build details details
def run_amber_test(input_dir, output_dir, each_cfg_option, amber_build_path, amber_build_flags):
    current_test_results = []

    # prepare to name each file according to the level of saturation being done
    saturation_level = each_cfg_option.get_saturation_level()
    if saturation_level == 0:
        output_file_name_extension = "no_saturation"
    elif saturation_level == 1:
        output_file_name_extension = "round_robin"
    elif saturation_level == 2:
        output_file_name_extension = "chunking"
    else:
        output_file_name_extension = "_" + str(saturation_level) + "level_saturation"

    # iterate over all files in the input directory and create a .amber file for each .txt file
    for file_name in os.listdir(input_dir):
        if file_name.endswith('.txt'):
            # input file name shouldn't end with .amber as the amber_test_generation.py script will add the extension
            output_file_name = file_name[:-4] + "_txt_" + output_file_name_extension
            input_file_name = input_dir + "/" + file_name
            log_print("generating amber test for: " + input_file_name)
            log_print("in")
            log_print(output_file_name)
            amber_test_generation.generate_amber_test(input_file_name, output_file_name, each_cfg_option)

            output_file_name = output_file_name + ".amber"

            # generate the command to run the amber test and place the results in a file temporarily
            run__test = amber_build_path + output_file_name + amber_build_flags + "> temp_results.txt"
            log_print("running test: " + output_file_name)
            log_print(run__test)
            os.system(run__test)

            # analyze the results of the temporary file to determine whether the test passed (P) or failed (F)
            with open('temp_results.txt', 'r') as file:
                results = file.read()
                test_iteration = file_name[:-4]
                if "1 pass" in results:
                    log_print("P")
                    temp_item = [test_iteration, "P"]
                    current_test_results.append(temp_item)
                elif "1 fail" in results:
                    log_print("F")
                    temp_item = [test_iteration, "F"]
                    current_test_results.append(temp_item)

            # create a directory of the amber test scripts generated at the specified output directory
            log_print("")
            move_amber_test_file = "mv " + output_file_name + " " + output_dir
            os.system(move_amber_test_file)

    os.system("rm -f temp_results.txt")

    return current_test_results


# main driver function to create amber files with the specified list of configuration objects, provided
# input directory, and details of the build path/type
def amber_driver(all_config_variants, input_dir, output_dir, amber_build_path, amber_build_flags):
    results = []
    # iterate over each configuration type and run directory of txt files with each configuration using run_amber_test()
    for each_cfg_option in all_config_variants:
        temp_results = run_amber_test(input_dir, output_dir, each_cfg_option, amber_build_path, amber_build_flags)
        results.append(temp_results)

    # verify that the results based off of each of the configuration settings are the same size to ensure all tests ran
    default_config_length = len(results[0])
    for result in results:
        current_length = len(result)
        if current_length != default_config_length:
            print("The number of results from all of the configuration settings must be the same", file=sys.stderr)
            exit(1)

    final_results = []

    # group the test results for each input file together based off of the test numbers
    for i in range(default_config_length):
        current_list = [i]

        for each_config_result in results:
            for each_test in each_config_result:
                if int(each_test[0]) == i:
                    current_list.append(each_test[1])
                    break
        final_results.append(current_list)

    log_print("")
    log_print("Finished running tests!")
    log_print("")

    format_output_results(final_results, all_config_variants, output_dir)


# output the final results into a formatted table presented in a .txt file and a .csv file
def format_output_results(final_results, all_config_variants, output_dir):
    today = date.today()
    todaydate = today.strftime("%Y-%m-%d")
    output_name_txt = output_dir +"/" + "final_results-" + todaydate + ".txt"
    output_name_csv = output_dir +"/" + "final_results-" + todaydate + ".csv"

    # create a list of headers for the output files based off of the configuration types used
    headers = ["Test File Name"]
    for each_config in all_config_variants:
        current_saturation = each_config.get_saturation_level()
        if current_saturation == 0:
            headers.append("No saturation Result")
        elif current_saturation == 1:
            headers.append("Round Robin Saturation Result")
        elif current_saturation == 2:
            headers.append("Chunking Saturation Result")
        else:
            headers.append(str(current_saturation))

    # open and write results to the .txt file
    output_file_txt = open(output_name_txt, "w+")
    log_print("writing ascii table to:")
    log_print(output_name_txt)
    log_print("")
    output_file_txt.write(tabulate(final_results, headers=headers, tablefmt="fancy_grid"))
    output_file_txt.write("\n")
    output_file_txt.close()
    
    log_print("writing csv table to:")
    log_print(output_name_csv)
    log_print("")

    # open and write resilts to the .csv file
    with open(output_name_csv, "w") as csv_file:
        writer = csv.writer(csv_file, delimiter=',')

        writer.writerow(headers)

        for line in final_results:
            writer.writerow(line)
    csv_file.close()

def find_amber():
    for a in AMBER_PATHS:
        cmd = "which " + a + " > /dev/null"
        ret = os.system(cmd)
        if ret == 0:
            log_print("found amber executable: ")
            log_print(a)
            log_print("")
            return a
    log_print("unable to find an amber executable")
    assert(0)

def get_new_dir_name():
    base_name = "results/output"
    label=0
    while(1):
        check_name = base_name + str(label)
        if not os.path.exists(check_name):
            print("writing results to:")
            print(check_name)
            print("")
            return check_name
        label+=1
    

def main():
    global LOG_FILE
    if len(sys.argv) != 2:
        print("Please provide a directory of .txt files to parse and process into Amber tests", file=sys.stderr)
        exit(1)

    start = time.time()

    input_dir = sys.argv[1]
    # the user must input the location of the directory where the .amber files will reside
    output_dir_path = get_new_dir_name()
    # the user must input the location of where the amber build path is located
    # the user may change the flags used to build the amber tests with
    amber_build_flags = " -d "

    os.system("mkdir " + output_dir_path)

    log_file_name = output_dir_path + "/output_log.txt"
    LOG_FILE = open(log_file_name, 'w')
    log_print("Date and Time:")
    now = datetime.now()
    nowpp = now.strftime("%d/%m/%Y %H:%M:%S")
    log_print(nowpp)
    log_print("Computer:")
    log_print(socket.gethostname())
    log_print("")
    vulkan_info = output_dir_path + "/vulkaninfo.txt"
    log_print("storing vulkaninfo to: " + vulkan_info)
    log_print("")
    os.system("vulkaninfo > " + vulkan_info)

    amber_build_path = find_amber() + " "    


    # the user must provide all the possible configuration objecs they want to test with and place them in the
    # all_config_variants list below
    default_config = Configuration(timeout=2000, workgroups=65532, threads_per_workgroup=1, saturation_level=0)
    round_robin_cfg = Configuration(timeout=2000, workgroups=65532, threads_per_workgroup=1, saturation_level=1)
    chunking_cfg = Configuration(timeout=2000, workgroups=65532, threads_per_workgroup=1, saturation_level=2)

    all_config_variants = [default_config, round_robin_cfg, chunking_cfg]

    # call the main driver function
    amber_driver(all_config_variants, input_dir, output_dir_path, amber_build_path, amber_build_flags)
    end = time.time()
    log_print("")
    log_print("Execution time (s):")
    log_print(str(end - start))
    LOG_FILE.close()


if __name__ == "__main__":
    main()
