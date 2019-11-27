import sys, os, subprocess


def open_file_with_default_program(filename, filepath):
    cwd = os.getcwd()
    try:
        os.chdir(filepath)
        if sys.platform.startswith('linux'):
            open_command = 'xdg-open'
            subprocess.run([open_command, filename + ".pdf"])
        else:
            open_command = 'start'
            subprocess.run([open_command, filename + ".pdf"], shell=True)
    finally:
        os.chdir(cwd)
