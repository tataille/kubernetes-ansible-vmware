import os
import sys
import subprocess
import argparse

# Constants
PLATFORM = sys.platform




def show(msg):
    """Local print() function."""
    print(msg)


def gen_key(user):
    """Generate a SSH Key."""
    # Genarate private key
    command = "yes y | ssh-keygen -t rsa -b 4096 -C {0} -f id_vm_rsa -P ''".format(user)
    subprocess.call(command, shell=True)


def push_key(user, host, port=22):
    if "ssh-copy-id" in os.listdir("/usr/local/bin"):
        show("SSH key found. Pushing key to remote server")
        command = "ssh-copy-id -p %s %s@%s" % (port, user, host)
        subprocess.call(command, shell=True)
            


def main():
    """Start of script."""
    parser = argparse.ArgumentParser(
        description="Uses the ssh-keygen and ssh-copy-id commands found on Mac and Linux systems. Mac Users will need to install ssh-copy-id before attempting to use this script. If you do not have Homebrew installed, please visit https://github.com/beautifulcode/ssh-copy-id-for-OSX for the install. If you do have Homebrew installed, run the command brew install ssh-copy-id in Terminal.")
    parser.add_argument("action", choices=[
                        "GenKey", "PushKey"], help="Action to be preformed")
    parser.add_argument("-u", "--user", help="SSH username")
    parser.add_argument("-s", "--host", help="IP or FQDN of server")
    parser.add_argument("-p", "--port", help="SSH port number")
    args = parser.parse_args()
    if (args.action == "GenKey"):
        gen_key(args.user)
    elif (args.action == "PushKey"):
        if args.user and args.host:
            if args.port:
                push_key(args.user, args.host, args.port)
            else:
                push_key(args.user, args.host)
        else:
            show("-u and -s are required for action PushKey. Use -h for Help.")

if __name__ == "__main__":
    main()