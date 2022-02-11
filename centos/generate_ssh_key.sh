# Check for Existing Keys
ls -l ~/.ssh/id_*.pub

# Verify SSH is Installed
ssh -V

# Create SSH Key Pair -- 4096-bit key
ssh-keygen -t rsa -b 4096


# Copy Public Key Using ssh-copy-id
ssh-copy-id username@remote_host
# Copy Public Key Using Secure Copy

# First, set up an SSH connection with the remote user:
ssh username@remote_host

# Next, create the ~/.ssh directory as well as the authorized_keys file:
mkdir -p ~/.ssh && touch ~/.ssh/authorized_keys

# Use the chmod command to change the file permission:
# chmod 700 makes the file executable, while chmod 600 allows the user to read and write the file.
chmod 700 ~/.ssh && chmod 600 ~/.ssh/authorized_keys
