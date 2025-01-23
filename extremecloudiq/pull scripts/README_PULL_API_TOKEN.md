Here's how you can securely store the username and password on Debian and allow any user to run the script:

Use Environment Variables:

Store the username and password in a file that is only readable by the root user.
Export these variables in the .bashrc or .profile file of the root user.

    echo "export API_USER='your_username'" >> /root/.bashrc
    echo "export API_PASS='your_password'" >> /root/.bashrc

Create a Wrapper Script:

Create a wrapper script that loads the environment variables and then runs the Python script.

    #!/bin/bash
    source /root/.bashrc
    python3 /path/to/xiq_pull_api_token.py

Make this script executable:

    chmod +x /path/to/wrapper_script.sh

Set the Correct Permissions:

Ensure the wrapper script can be executed by all users, but the file with the environment variables can only be read by the root user.

    chmod 755 /path/to/wrapper_script.sh
    chmod 600 /root/.bashrc

Use sudo for the Script:

Configure sudo to allow the script to be run without a password prompt. Add a rule in the /etc/sudoers file:

    ALL ALL=(ALL) NOPASSWD: /path/to/wrapper_script.sh

This method ensures that the username and password are stored securely while allowing any user to execute the script.