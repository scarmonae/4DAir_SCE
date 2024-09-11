#!/bin/bash

DATA_DIR="/home/medico_eafit/WORKSPACES/sebastian_carmona/data/EAFIT/Dataset1/LiMon_Raw_Data_cc"
ANALYSIS_SCRIPT_DIR="/home/medico_eafit/WORKSPACES/sebastian_carmona/REPOSITORIOS/LPP/Lidar_Analysis_PDL2/"
CONF_FILE="/home/medico_eafit/WORKSPACES/sebastian_carmona/data/EAFIT/analysisParameters_Medellin_jp.conf"

cd "$ANALYSIS_SCRIPT_DIR"

process_day() {
    local day_dir="$1"
    # printf "%s\n" "$day_dir"
    sudo ./lidarAnalysis_PDL2 "${day_dir}/LPP/L1.nc" "${day_dir}/LPP/L2.nc" "/home/medico_eafit/WORKSPACES/sebastian_carmona/data/EAFIT/analysisParameters_Medellin_jp.conf" #|| printf "Error processing directory: %s\n" "$day_dir" >&2
}

export -f process_day

main() {
    find "$DATA_DIR" -mindepth 3 -maxdepth 3 -type d -exec bash -c 'process_day "$0"' {} \;
}

main "$@"
