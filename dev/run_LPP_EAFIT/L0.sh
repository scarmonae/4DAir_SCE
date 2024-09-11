#!/bin/bash

cd "/home/medico_eafit/WORKSPACES/sebastian_carmona/REPOSITORIOS/LPP/Lidar_Analysis_PDL0"

DATA_DIR="/home/medico_eafit/WORKSPACES/sebastian_carmona/data/EAFIT/Dataset1/LiMon_Raw_Data_cc"

process_day() {
    local day_dir="$1"

    # Create the LPP directory if it does not exist
    mkdir -p "${day_dir}/LPP"
    
    local rs_dir="${day_dir}/RS"
    local dc_dir="${day_dir}/DC"
    
    if [[ -d "$rs_dir" && -d "$dc_dir" ]]; then
        sudo ./lidarAnalysis_PDL0 "${rs_dir}/" "${day_dir}/LPP/L0.nc" "/home/medico_eafit/WORKSPACES/sebastian_carmona/data/EAFIT/analysisParameters_Medellin_jp.conf"
    elif [[ ! -d "$rs_dir" ]]; then
        local file_count
        file_count=$(find "$day_dir" -maxdepth 1 -type f | wc -l)
        
        if [[ "$file_count" -gt 10 ]]; then
            sudo ./lidarAnalysis_PDL0 "$day_dir" "${day_dir}/LPP/L0.nc" "/home/medico_eafit/WORKSPACES/sebastian_carmona/data/EAFIT/analysisParameters_Medellin_jp.conf"
        else
            printf "10 or fewer files found in: %s\n" "$day_dir"
        fi
    fi
}

export -f process_day

main() {
    find "$DATA_DIR" -mindepth 3 -maxdepth 3 -type d -exec bash -c 'process_day "$0"' {} \;
}

main "$@"
