# Amber-Testing-Framework
This repository contains scripts to automatically generate amber tests for formatted input files along with examples of test cases

Repository Organization:

Amber_2_Thread_2_Instruction_2_instruction_Tests:
	- Contains subdirectories of 2 thread, 2 instruction tests labeled according to the test number. Each subdirectory contains the .txt 	  file and associated amber tests

Amber_2_Thread_2_Instruction_3_instruction_Tests:
	- Contains subdirectories of 2 thread, 3 instruction tests labeled according to the test number. Each subdirectory contains the .txt 	  file and associated amber tests

Amber_Driver_Results:
	- Contains subdirectories of the results from the amber_test_driver.py script. Each subdirectory contains the .txt and .csv output   	  tables

Input_Files:
	- Contains subdirectories of the input .txt files necessary to run the scripts with




Running the scripts:

amber_test_generation.py script: python3 amber_test_generation.py input_file output_file_name 
	- Note 1: the output_file_name should not end with ".amber" as the script will automatically add that extension to the provided name)
	- Note 2: Make sure configuration.py is in the same working directory as amber_test_generation.py

amber_test_driver.py script: python3 amber_test_driver.py directory_of_input_files
	- Note 1: Some of the paths and flags need to be edited in main() based off of where the script is being run relative to amber build 

configuration.py: Configuration object that is used in the scripts above


 