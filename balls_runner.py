import os
import sys

dry_run = '--dry-run' in sys.argv
local   = '--local' in sys.argv
detach  = '--detach' in sys.argv

dry_run = True
local = False
detach = True

if not os.path.exists("slurm_logs"):
    os.makedirs("slurm_logs")

if not os.path.exists("slurm_scripts"):
    os.makedirs("slurm_scripts")


networks_prefix = "networks"

base_networks = {
    }


# Don't give it a save name - that gets generated for you
# jobs = [
#         {
#             "import": "onestep",
#         },
#
#
#     ]

jobs = []

# noise_options = [0.1]
# sharpening_rate_options = [10]
learning_rate_options = [40e-5, 50e-5]
heads_options = [1,2,3]
numballs_options = [2,3]
subsamp_options = [3]
# L2_options = [1e-2, 1e-3, 1e-4]

# for noise in noise_options:
# for sharpening_rate in sharpening_rate_options:
for learning_rate in learning_rate_options:
    for numballs in numballs_options:
        for heads in heads_options:
            for subsamp in subsamp_options:
                job = {
                            # "noise": noise,
                            # "sharpening_rate": sharpening_rate,
                            "learning_rate": learning_rate,
                            "heads": heads,
                            "numballs": numballs,
                            "subsample":subsamp
                            # "dataset_name": dataset_name
                            # "gpu": True,
                        }
                jobs.append(job)


if dry_run:
    print "NOT starting jobs:"
else:
    print "Starting jobs:"

for job in jobs:
    jobname = "balls"
    flagstring = ""
    for flag in job:
        if isinstance(job[flag], bool):
            if job[flag]:
                jobname = jobname + "_" + flag
                flagstring = flagstring + " --" + flag
            else:
                print "WARNING: Excluding 'False' flag " + flag
        elif flag == 'import':
            imported_network_name = job[flag]
            if imported_network_name in base_networks.keys():
                network_location = base_networks[imported_network_name]
                jobname = jobname + "_" + flag + "_" + str(imported_network_name)
                flagstring = flagstring + " --" + flag + " " + str(network_location)
            else:
                jobname = jobname + "_" + flag + "_" + str(job[flag])
                flagstring = flagstring + " --" + flag + " " + networks_prefix + "/" + str(job[flag])
        else:
            jobname = jobname + "_" + flag + "_" + str(job[flag])
            flagstring = flagstring + " --" + flag + " " + str(job[flag])
    flagstring = flagstring + " --name " + jobname

    jobcommand = "th balls_main.lua" + flagstring

    print(jobcommand)
    if local and not dry_run:
        if detach:
            os.system(jobcommand + ' 2> slurm_logs/' + jobname + '.err 1> slurm_logs/' + jobname + '.out &')
        else:
            os.system(jobcommand)

    else:
        with open('slurm_scripts/' + jobname + '.slurm', 'w') as slurmfile:
            slurmfile.write("#!/bin/bash\n")
            slurmfile.write("#SBATCH --job-name"+"=" + jobname + "\n")
            slurmfile.write("#SBATCH --output=slurm_logs/" + jobname + ".out\n")
            # slurmfile.write("#SBATCH --error=slurm_logs/" + jobname + ".err\n")
            slurmfile.write("#SBATCH -N 1\n")
            slurmfile.write("#SBATCH -c 2\n")
            slurmfile.write("#SBATCH -p gpu\n")
            slurmfile.write("#SBATCH --gres=gpu:1\n")
            slurmfile.write("#SBATCH --mem=30000\n")
            slurmfile.write("#SBATCH --time=6-23:00:00\n")
            slurmfile.write("#SBATCH -x node027\n")
            slurmfile.write(jobcommand)

        if not dry_run:
            # if 'gpu' in job and job['gpu']:
            #     os.system("sbatch -N 1 -c 2 --gres=gpu:1 -p gpu --mem=8000 --time=6-23:00:00 slurm_scripts/" + jobname + ".slurm &")
            # else:
            #     os.system("sbatch -N 1 -c 2 --mem=8000 --time=6-23:00:00 slurm_scripts/" + jobname + ".slurm &")
            os.system("sbatch slurm_scripts/" + jobname + ".slurm &")
