correct_req_file = input("Correct requirements file: ")
additional_req_file = input("Additional requirements file: ")

with open(correct_req_file, "r") as f:
    correct_req = f.readlines()

with open(additional_req_file, "r") as f:
    additional_req = f.readlines()

# Remove the requirements that are already in the correct requirements file
req_to_remove = [req for req in additional_req if req not in correct_req]

# Write the requirements to remove to a file
with open("req_to_remove.txt", "w") as f:
    f.write("\n".join(req_to_remove))


