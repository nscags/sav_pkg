#!/bin/bash
#SBATCH -J bear_sav_matrix                               # Name of program
#SBATCH -o matrix_%a.out                            # Name of output file (%a = array task id)
#SBATCH --array=0-31                                # One task per matrix.MATRIX entry
# #SBATCH -p lo-core                                # Partition (general, lo-core)
# #SBATCH --time=72:00:00                           # Timeout after 72 hours (lo-core), 12 hours (general)
#SBATCH -n 40                                       # Asking for cores
#SBATCH --mail-type=ALL                             # Event(s) that triggers email notification (BEGIN,END,FAIL,ALL)
#SBATCH --mail-user=nicholas.scaglione@uconn.edu    # Destination email address
#SBATCH --mem=128G                                  # Request RAM

# Source Virtual Environment
source ~/sav/venv_latest/bin/activate

export PYTHONHASHSEED=0

# SLURM_ARRAY_TASK_ID selects the combo from scripts/matrix.py:MATRIX
# and also seeds randomness for that combo (see run_matrix.py)
python3 ~/sav/sav_pkg/scripts/run_matrix.py "$@"   # e.g. --trials 5 for a test run
