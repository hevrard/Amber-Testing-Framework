# -----------------------------------------------------------------------
# amber_two_thread_tests.py
# Author: Hari Raval
# -----------------------------------------------------------------------
import sys
import re


# write the necessary "boiler plate" code to generate an amber test, along with a Shader
# Storage Buffer Object with two memory locations, workgroup size, and global variable to
# assign thread IDs. output is the file being written to and timeout determines (in ms) when the
# program will terminate in the case the GPU hangs
def amber_prologue(output, timeout, thread0_instructions, thread1_instructions):
    output.write("#!amber\n")
    output.write("\n")
    output.write("SET ENGINE_DATA fence_timeout_ms " + timeout + "\n")
    output.write("\n")
    output.write("SHADER compute test GLSL\n")
    output.write("#version 430\n")
    output.write("\n")
    output.write("layout(set = 0, binding = 0) volatile buffer TEST {\n")
    output.write("\tuint x;\n")
    output.write("} test; \n")
    output.write("\n")
    output.write("layout(local_size_x = 1, local_size_y = 1, local_size_z = 1) in;\n")
    output.write("\n")
    output.write("void main()\n")
    output.write("{\n")
    output.write("\tuint gid_x = gl_GlobalInvocationID.x;\n")
    output.write("\tint pc = 0;\n")
    output.write("\tif (gid_x == 0) { \n")
    output.write("\t   int terminate = 0;\n")
    output.write("\n")
    handle_thread(thread0_instructions, output)
    output.write("}\n")
    output.write("\telse if (gid_x = 1) { \n")
    output.write("\t   int terminate = 0;\n")
    output.write("\n")
    handle_thread(thread1_instructions,output)
    output.write("  }\n")
    output.write("}\n")


# generate the appropriate instructions to write to the amber file (output) for the provided thread and its
# pseudo instructions ,thread_instructions
def handle_thread(thread_instructions, output):
    # this pattern searches for the arguments in the provided instruction, in between  "(" and ")"
    pattern = "\\((.+?)\\)"
    search_pattern = re.search(pattern, thread_instructions[0])
    numerical_representation = " "
    if search_pattern:
        numerical_representation = search_pattern.group(1)

    # create a list of the arguments that are provided from the pseudo instruction
    numerical_representation = numerical_representation.split(",")

    # handle the case of atomic_exch_branch() instruction
    if thread_instructions[0].startswith("atomic_exch_branch"):

        # note the memory_location and instruction_address values are not needed, since we are assuming writing to the
        # same memory location and the loop is back to the current instruction address
        memory_location = numerical_representation[0]
        check_value = numerical_representation[1]
        exchange_value = numerical_representation[2]
        instruction_address = numerical_representation[3]
        output.write("\t while (true) {\n")
        output.write("\t   if (terminate == 1) {\n")
        output.write("\t   break;\n")
        output.write("\t}\n")
        output.write("\tswitch(pc) {\n")
        output.write("\t\tcase 0: \n")
        output.write("\t\t if (atomicExchange(test.x, " + exchange_value + ") ==  " + check_value + ") { \n")
        output.write("\t\t\tpc = 0;\n")
        output.write("\t\t}\n")
        output.write("\t\t else {\n")
        output.write("\t\t\t pc = 1;\n")
        output.write("\t\t }\n")
        output.write("\t\t\t break;\n")
        output.write("\t\tcase 1:\n")
        output.write("\t\t\tterminate = 1;\n")
        output.write("\t\t\tbreak;\n")
        output.write("\t\t}\n")
        output.write("\t}\n")
        #output.write("\t}\n") # remove this and put in prologue
        output.write("\n")

    # handle the case of atomic_chk_branch() instruction
    elif thread_instructions[0].startswith("atomic_chk_branch"):

        # note the memory_location and instruction_address values are not needed, since we are assuming writing to the
        # same memory location and the loop is back to the current instruction address
        memory_location = numerical_representation[0]
        check_value = numerical_representation[1]
        instruction_address = numerical_representation[2]

        output.write("\t while (true) {\n")
        output.write("\t   if (terminate == 1) {\n")
        output.write("\t   break;\n")
        output.write("\t}\n")
        output.write("\tswitch(pc) {\n")
        output.write("\t\tcase 0: \n")
        output.write("\t\t if (atomicAdd(test.x, 0) == " + check_value + " ) { \n")
        output.write("\t\t\tpc = 0;\n")
        output.write("\t\t}\n")
        output.write("\t\t else {\n")
        output.write("\t\t\t pc = 1;\n")
        output.write("\t\t }\n")
        output.write("\t\t break;\n")
        output.write("\t\tcase 1:\n")
        output.write("\t\t\tterminate = 1;\n")
        output.write("\t\t\tbreak;\n")
        output.write("\t\t}\n")
        output.write("\t}\n")
        output.write("\n")  # one more closing bracket after this...

    # handle the case of atomic_store() instruction
    elif thread_instructions[0].startswith("atomic_store"):
        # note the memory_location is not needed, since we are looping back to the current instruction address
        memory_location = numerical_representation[0]
        write_value = numerical_representation[1]
        output.write("\t while (true) {\n")
        output.write("\t   if (terminate == 1) {\n")
        output.write("\t   break;\n")
        output.write("\t}\n")
        output.write("\tswitch(pc) {\n")
        output.write("\t\tcase 0: \n")
        output.write("\t\tatomicExchange(test.x, " + write_value + ");\n")
        output.write("\t\t\tpc = pc + 1;\n")
        output.write("\t\tbreak;\n")
        output.write("\t\tcase 1:\n")
        output.write("\t\t\tterminate = 1;\n")
        output.write("\t\t\tbreak;\n")
        output.write("\t\t}\n")
        output.write("\t}\n")


# write the necessary "boiler plate" code to end the amber test, along with generating the number of threads and doing
# a sanity check that all threads executed
def amber_epilogue(output):
    output.write("\n")
    output.write("END\n")
    output.write("\n")
    output.write("BUFFER tester DATA_TYPE uint32 SIZE 1 FILL 0\n")
    output.write("\n")
    output.write("PIPELINE compute test_pipe\n")
    output.write("  ATTACH test\n")
    output.write("  BIND BUFFER tester AS storage DESCRIPTOR_SET 0 BINDING 0 \n")
    output.write("\n")
    output.write("END\n")
    output.write("\n")
    output.write("RUN test_pipe 65535 1 1\n")


# main() will act as a driver function to generate an amber test. Currently, two-threaded and three-instruction tests
# are supported. The program must be run with two command line arguments, in the following order: the name of the txt
# file for which a test will be generated for and the time (in ms) for which the test should run for before termination
def main():
    if len(sys.argv) != 3:
        print("Please input the correct number of arguments", file=sys.stderr)
        exit(1)

    # read in the appropriate arguments from the command line
    input_alloy_txt_file = open(sys.argv[1], "r")
    timeout = sys.argv[2]

    # create a cleaned up list of the file that is read in as input
    all_lines = input_alloy_txt_file.readlines()
    components = []
    for line in all_lines:
        if line != "\n":
            components.append(line)

    cleaned_components = [x[:-1] for x in components]

    # lists to hold the instructions for the two threads
    thread0_instructions = []
    thread1_instructions = []

    # store the appropriate instruction(s) to the appropriate thread's list
    for index, item in enumerate(cleaned_components):
        if item == "THREAD0":
            # ask for the changed input file format, so this will be cleaner and can handle any number of instructions
            thread0_instructions.append(cleaned_components[index + 1])
        if item == "THREAD1":
            thread1_instructions.append(cleaned_components[index + 1])

    # name and open the output file to contain the amber test case
    output_amber_file = sys.argv[1]
    output_amber_file = output_amber_file.replace(".", "_")
    output_amber_file = output_amber_file + ".amber"
    output = open(output_amber_file, "a")

    # call all helper funcions to generate the test case
    amber_prologue(output, timeout, thread0_instructions, thread1_instructions)
    amber_epilogue(output)


if __name__ == "__main__":
    main()
