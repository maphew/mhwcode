''' Quick and dirty script to measure execution time of a command.

    Sources:
        http://stackoverflow.com/questions/1465146/how-do-you-determine-a-processing-time-in-python
        http://www.cyberciti.biz/faq/python-run-external-command-and-get-output
'''
import sys
import timeit
import subprocess

cmd = sys.argv[1]
cmd_args = sys.argv[2:]


tic = timeit.default_timer()

# run the command
p = subprocess.Popen(cmd, stderr=subprocess.PIPE, shell=True)

# do not wait cmd finish, start displaying output immediately
while True:
    out = p.stderr.read(1)
    if out == '' and p.poll() != None:
        break
    if out != '':
        sys.stdout.write(out)
        sys.stdout.flush()

toc = timeit.default_timer()
print("Run time (secs):"), (toc - tic)