#!/bin/bash

cd "/home/medico_eafit/WORKSPACES/sebastian_carmona/REPOSITORIOS/LPP/Lidar_Analysis_PDL0"

DATA_DIR="/home/medico_eafit/WORKSPACES/sebastian_carmona/data/EAFIT/Dataset1/LiMon_Raw_Data_cc"

generate_output_filename() {
    local day_dir="$1"
    local prefix="LIDAR"
    local location="MED"
    local version="EAFIT"
    local variable="LO"
    
    # Extract date and time from the binary filenames
    local datetime
    datetime=$(find "$day_dir" \( -name "*.RS*" -o -name "*.DC*" \) -exec basename {} \; | head -n 1 | sed -E 's/^[^0-9]*([0-9]{8})\.([0-9]{6}).*$/\1_\2/')
    
    if [[ -z "$datetime" ]]; then
        datetime=$(date +"%Y%m%d_%H%M%S")
    fi
    
    local output_filename="${prefix}_${datetime}_${location}_${version}_${variable}.nc"
    printf "%s" "$output_filename"
}

process_day() {
    local day_dir="$1"

    # Create the LPP directory if it does not exist
    mkdir -p "${day_dir}/LPP"
    
    local rs_dir="${day_dir}/RS"
    local dc_dir="${day_dir}/DC"
    local output_file
    output_file=$(generate_output_filename "$day_dir")
    
    printf "Processing directory: %s\n" "$day_dir"
    printf "Output file will be: %s\n" "${day_dir}/LPP/${output_file}"

    if [[ -d "$rs_dir" && -d "$dc_dir" ]]; then
        printf "" 
        # sudo ./lidarAnalysis_PDL0 "${rs_dir}/" "${day_dir}/LPP/${output_file}" "/home/medico_eafit/WORKSPACES/sebastian_carmona/data/EAFIT/analysisParameters_Medellin_jp.conf"
    elif [[ ! -d "$rs_dir" ]]; then
        local file_count
        file_count=$(find "$day_dir" -maxdepth 1 -type f | wc -l)
        
        if [[ "$file_count" -gt 10 ]]; then
            printf ""
            # sudo ./lidarAnalysis_PDL0 "$day_dir" "${day_dir}/LPP/${output_file}" "/home/medico_eafit/WORKSPACES/sebastian_carmona/data/EAFIT/analysisParameters_Medellin_jp.conf"
        else
            printf "10 or fewer files found in: %s\n" "$day_dir"
        fi
    fi
}

export -f generate_output_filename
export -f process_day

main() {
    find "$DATA_DIR" -mindepth 3 -maxdepth 3 -type d -exec bash -c 'process_day "$0"' {} \;
}

main "$@"
