#!/bin/bash
#SBATCH -J bspp_aspa                                      # Name of program
#SBATCH -o log_bspp_aspa.out                              # Name of output file
# #SBATCH -p lo-core                                  # Partition (general, lo-core)
# #SBATCH --time=72:00:00                             # Timeout after 72 hours (lo-core), 12 hours (general)
#SBATCH -n 20                                       # Asking for cores
#SBATCH --mail-type=ALL                             # Event(s) that triggers email notification (BEGIN,END,FAIL,ALL)
#SBATCH --mail-user=nicholas.scaglione@uconn.edu    # Destination email address
#SBATCH --mem=128G                                   # Request RAM
# #SBATCH --mem-per-cpu=16G                         # Request RAM per cpu core, had OOM errors

# Source Virtual Environment
source ~/sav/venv_latest/bin/activate

# Set Job Completion Index
export JOB_COMPLETION_INDEX=$SLURM_ARRAY_TASK_ID
export PYTHONHASHSEED=$SLURM_ARRAY_TASK_ID
# PYTHONHASHSEED=$SLURM_TASK_ID

# Run the simulation
python3 ~/sav/sav_pkg/scripts/bspp_aspa.py
