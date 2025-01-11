import subprocess

# Path to your main script
script_path = "main.py"

# Launch two instances of the script
process1 = subprocess.Popen(["python", script_path])
process2 = subprocess.Popen(["python", script_path])

# Wait for both processes to finish
process1.wait()
process2.wait()
