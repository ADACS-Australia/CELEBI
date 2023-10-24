import platform

# Specify the file name
file_name = 'version.txt'

# Open the file with write ('w') permission.
# If the file doesn't exist, Python will create it.
with open(file_name, 'w') as file:
    # Write the Python version to the file
    file.write(platform.python_version())

