#!/bin/bash
name=$1  

# Source virtual environment
source ~/sav/venv/bin/activate

# Set any environment variables
export JOB_COMPLETION_INDEX=$SLURM_ARRAY_TASK_ID
export PYTHONHASHSEED=$JOB_COMPLETION_INDEX

# Run the actual Python simulation
python3 ~/sav/sav_pkg/scripts/sim_${name}.py
