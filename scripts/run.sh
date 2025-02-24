#!/bin/bash
#SBATCH -p lo-core
#SBATCH --time=72:00:00                             # Timeout after 72 hours
#SBATCH -n 10                                       # Asking for 10 cores
#SBATCH --mail-type=ALL                             # Event(s) that triggers email notification (BEGIN,END,FAIL,ALL)
#SBATCH --mail-user=nicholas.scaglione@uconn.edu    # Destination email address
#SBATCH --mem=32G                                   # Request 32G of RAM
# #SBATCH --mem-per-cpu=16G
# #SBATCH -o log.out

# Source Virtual Environment
source ~/sav/venv/bin/activate

# Set Job Completion Index
export JOB_COMPLETION_INDEX=$SLURM_ARRAY_TASK_ID
export PYTHONHASHSEED=$JOB_COMPLETION_INDEX
# PYTHONHASHSEED=$SLURM_TASK_ID

# Run the simulation
python3 ~/sav/sav_pkg/scripts/sim_e2s.py