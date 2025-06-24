#!/bin/bash
# #SBATCH -p lo-core
# #SBATCH --time=72:00:00                             # Timeout after 72 hours
#SBATCH -n 80                                       # Asking for 80 cores
#SBATCH --mail-type=ALL                             # Event(s) that triggers email notification (BEGIN,END,FAIL,ALL)
#SBATCH --mail-user=nicholas.scaglione@uconn.edu    # Destination email address
#SBATCH --mem=128G                                  # Request 128G of RAM
# #SBATCH --mem-per-cpu=16G
#SBATCH -o log_dsr.out

# Source Virtual Environment
source ~/sav/venv/bin/activate

# Set Job Completion Index
export JOB_COMPLETION_INDEX=$SLURM_ARRAY_TASK_ID
export PYTHONHASHSEED=$JOB_COMPLETION_INDEX
# PYTHONHASHSEED=$SLURM_TASK_ID

# Run the simulation
python3 ~/sav/sav_pkg/scripts/sim_dsr.py