#!/bin/bash
#SBATCH -J precompute_routes                       # Name of program
#SBATCH -o precompute_routes_%j.out                # Name of output file (%j = job id, unique per run)
# #SBATCH --array=0-9                              # Uncomment (or pass --array) to split batches over N jobs
# #SBATCH -p lo-core                               # Partition (general, lo-core)
# #SBATCH --time=72:00:00                          # Timeout after 72 hours (lo-core), 12 hours (general)
#SBATCH -n 40                                      # Asking for cores (= worker processes)
#SBATCH --mail-type=ALL                            # Event(s) that triggers email notification (BEGIN,END,FAIL,ALL)
#SBATCH --mail-user=nicholas.scaglione@uconn.edu   # Destination email address
#SBATCH --mem=128G                                 # Request RAM

# Source Virtual Environment
source ~/sav/venv_latest/bin/activate

# Extra arguments are passed through, e.g.
#   sbatch run_precompute_routes.sh --num-origins 4000         (next 4000 origins)
#   sbatch --array=0-9 run_precompute_routes.sh --time-budget-h 11.5
# Task index/count and worker count come from SLURM_ARRAY_TASK_ID,
# SLURM_ARRAY_TASK_COUNT and SLURM_NTASKS.
python3 ~/sav/sav_pkg/scripts/precompute_routes.py "$@"
