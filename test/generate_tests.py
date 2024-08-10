import os
import subprocess

# Walk the source directory (/Users/john/src/code-rag/ragmatic/src/ragmatic) and 
# invoke the shell command `write-pytest FILEPATH > OUTPUT_DIR` using subprocess to generate test files in a directory
# structure that matches the structure of the source directory. Test files should have
# the same name as the source file with `test_` prepended.

ignore_files = ["__init__.py"]


def run_write_pytest_command(filepath, output_dir, module_root):
    print(f"Generating test for {filepath}")    
    command = f"write-pytest {filepath} {module_root} > {output_dir}"
    subprocess.run(command, shell=True)

def generate_tests(source_dir, output_dir):
    for root, dirs, files in os.walk(source_dir):
        for file in files:
            if file in ignore_files:
                continue
            if file.endswith(".py"):
                source_file = os.path.join(root, file)
                test_filename = f"test_{file}"
                test_dir = os.path.join(output_dir, os.path.relpath(root, source_dir))
                test_file = os.path.join(test_dir, test_filename)
                if not os.path.exists(test_dir):
                    print(f"Creating directory {test_dir}")
                    os.makedirs(test_dir, exist_ok=True)
                run_write_pytest_command(source_file, test_file, os.path.dirname(source_dir))

source_dir = "/Users/john/src/code-rag/ragmatic/src/ragmatic"
output_dir = "/Users/john/src/code-rag/ragmatic/test/package_tests"

if __name__ == "__main__":

    generate_tests(source_dir, output_dir)
