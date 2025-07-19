#!/bin/bash

# === Configuration Variables ===
name="apcna"
partition="lo-core"
time_limit="72:00:00"
num_tasks=40
mem="64G"
email="nicholas.scaglione@uconn.edu"
log_file="log_${name}.out"
script_to_run="run_sim.sh"

# === Submit SLURM Job Dynamically ===
sbatch \
  --job-name="$name" \
  --partition="$partition" \
  --time="$time_limit" \
  --ntasks="$num_tasks" \
  --mail-type=ALL \
  --mail-user="$email" \
  --mem="$mem" \
  --output="$log_file" \
  "$script_to_run" "$name"
