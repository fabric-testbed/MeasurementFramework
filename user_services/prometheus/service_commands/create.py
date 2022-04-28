# run the install scripts in instrumentize/ansible/playbook... etc
  
from datetime import datetime
import os
import subprocess

#ansible_dir =  "/home/mfuser/mf_git/instrumentize/ansible/fabric_experiment_instramentize"
#os.chdir(ansible_dir)
playbook_exe = "/home/mfuser/.local/bin/ansible-playbook"
#ansible_hosts_file = "/home/mfuser/mf_git/promhosts.ini"
ansible_hosts_file = '/home/mfuser/mf_git/instrumentize/ansible/fabric_experiment_instramentize/promhosts.ini'
playbook = "/home/mfuser/mf_git/instrumentize/ansible/playbook_fabric_experiment_install_prometheus.yml"
keyfile = "/home/mfuser/.ssh/mfuser"

# For some reason the local ansible.cfg file is not being used
os.environ["ANSIBLE_HOST_KEY_CHECKING"] = "False"

cmd = [playbook_exe, "-i", ansible_hosts_file, "--key-file", keyfile, "-b", playbook]

r = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

# print(r.returncode)
# print(r.stdout)
# print(r.stderr)

decoded_out = r.stdout.decode("utf-8")
play_recap = decoded_out[decoded_out.find("PLAY RECAP"):]
decoded_err = r.stderr.decode("utf-8")

if r.returncode == 0:
    print("Prometheus successfully installed.")
else:
    print("Prometheus install playbook failed.")

print(play_recap)


# Save the ansible output
now = datetime.now()
this_script_dir = os.path.dirname(os.path.realpath(__file__))
ansible_output_file = os.path.join( this_script_dir,  "experiment_install_prometheus_{0}".format( now.strftime("%b_%d_%Y_%H_%M_%S") ) )

#alphabetical order
ansible_output_file = os.path.join( this_script_dir,  "experiment_install_prometheus_{0}".format( now.strftime("%Y_%m_%d_%H_%M_%S") ) )


with open(ansible_output_file, "w") as aof:
    aof.write("STDOUT:\n")
    aof.write(decoded_out)
    aof.write("\nSTDERR:\n")
    aof.write(decoded_err)



# Save the ansible recap for easy access
ansible_recap_file = os.path.join( this_script_dir,  "experiment_install_prometheus_recap_{0}".format( now.strftime("%b_%d_%Y_%H_%M_%S") ) )

with open(ansible_recap_file, "w") as arf:
    arf.write(play_recap)




