import sys
import subprocess

# implement pip as a subprocess:
subprocess.check_call([sys.executable, '-m', 'pip', 'install',
'Pillow'])

subprocess.check_call([sys.executable, '-m', 'pip', 'install',
'Flask'])

subprocess.check_call([sys.executable, '-m', 'pip', 'install',
'json'])

subprocess.check_call([sys.executable, '-m', 'pip', 'install',
'requests'])