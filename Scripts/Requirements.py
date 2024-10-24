import pkg_resources

# Get the list of all installed packages
installed_packages = pkg_resources.working_set

# Prepare the list of installed packages and their versions
installed_packages_list = sorted([f"{pkg.key}=={pkg.version}" for pkg in installed_packages])

# Specify the output file name
output_file = "installed_modules_list.txt"

# Write the list to the file
with open(output_file, "w") as file:
    for package in installed_packages_list:
        file.write(package + "\n")

print(f"List of installed modules saved to {output_file}")
