#!/bin/bash
#SBATCH -J bspi_pp_alg_a_min_fp                     # Name of program
#SBATCH -o log_bspi_pp_alg_a_min_fp.out             # Name of output file
# #SBATCH -p lo-core                                # Partition (general, lo-core)
# #SBATCH --time=72:00:00                           # Timeout after 72 hours (lo-core), 12 hours (general)
#SBATCH -n 40                                       # Asking for cores
#SBATCH --mail-type=ALL                             # Event(s) that triggers email notification (BEGIN,END,FAIL,ALL)
#SBATCH --mail-user=nicholas.scaglione@uconn.edu    # Destination email address
#SBATCH --mem=128G                                  # Request RAM
# #SBATCH --mem-per-cpu=16G                         # Request RAM per cpu core, had OOM errors

# Source Virtual Environment
source ~/sav/venv_latest/bin/activate

# Set Job Completion Index
export JOB_COMPLETION_INDEX=0
export PYTHONHASHSEED=0

# Run the simulation
python3 ~/sav/sav_pkg/scripts/bspi_pp/bspi_pp_alg_a_min_fp.py
