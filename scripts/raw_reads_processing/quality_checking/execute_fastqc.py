import os
from common_aDNA_scripts import *

def get_threads_count_for_fastqc():
    # Get the number of threads from the config file
    threads = config['processing']['fastqc']['threads']

    if threads is None or not isinstance(threads, int) or threads <= 0:
        return 1  # Default to 1 thread if not specified or invalid
    
    return threads

def fastqc_for_species(species: str):
    # run fastqc for raw data
    fastqc_for_raw_data(species)

    # run fastqc for trimmed data
    fastqc_for_adapter_removed_data(species)

    # run fastqc for quality filtered data
    fastqc_for_quality_filtered_data(species)

    # run fastqc for duplicates removed data
    fastqc_for_duplicates_removed_data(species)

def fastqc_for_raw_data(species: str):
    print_info(f"Running fastqc for species {species} raw data")

    # raw data
    raw_reads_folder = get_folder_path_species_raw_reads(species)
    output_folder = get_folder_path_species_results_qc_fastqc_raw(species)

    raw_reads_files = get_files_in_folder_matching_pattern(raw_reads_folder, f"*{FILE_ENDING_FASTQ_GZ}")

    files_list = get_files_in_folder_matching_pattern(output_folder, f"*{FILE_ENDING_FASTQC_HTML}")

    if len(files_list) > 0:
        print_info(f"Fastqc for raw already exists for species {species}. Skipping.")
        return
    
    if len(raw_reads_files) == 0:
        print_warning(f"No raw reads found for species {species}. Skipping.")
        return
    
    execute_fastqc(species, raw_reads_files, output_folder)

    print_success(f"fastqc for species {species} raw data complete")

def fastqc_for_quality_filtered_data(species: str):
    print_info(f"Running fastqc for species {species} quality filtered data")

    quality_filtered_reads_folder = get_folder_path_species_processed_quality_filtered(species)
    output_folder = get_folder_path_species_results_qc_fastqc_quality_filtered(species)

    quality_filtered_reads = get_files_in_folder_matching_pattern(quality_filtered_reads_folder, f"*{FILE_ENDING_QUALITY_FILTERED_FASTQ_GZ}")

    files_list = get_files_in_folder_matching_pattern(output_folder, f"*{FILE_ENDING_FASTQC_HTML}")

    if len(files_list) > 0:
        print_info(f"Fastqc for quality filtered already exists for species {species}. Skipping.")
        return
    
    if len(quality_filtered_reads) == 0:
        print_warning(f"No quality filtered reads found for species {species}. Skipping.")
        return
    
    execute_fastqc(species, quality_filtered_reads, output_folder)

    print_success(f"fastqc for species {species} quality filtered data complete")

def fastqc_for_adapter_removed_data(species: str):
    print_info(f"Running fastqc for species {species} adapter removed data")

    #adapter removed data
    trimmed_reads_folder = get_folder_path_species_processed_adapter_removed(species)
    output_folder = get_folder_path_species_results_qc_fastqc_adapter_removed(species)

    adapter_removed_reads = get_files_in_folder_matching_pattern(trimmed_reads_folder, f"*{FILE_ENDING_ADAPTER_REMOVED_FASTQ_GZ}")

    files_list = get_files_in_folder_matching_pattern(output_folder, f"*{FILE_ENDING_FASTQC_HTML}")

    if len(files_list) > 0:
        print_info(f"fastqc for adapter removed already exists for species {species}. Skipping.")
        return
    
    if len(adapter_removed_reads) == 0:
        print_warning(f"No adapter removed reads found for species {species}. Skipping.")
        return
    
    execute_fastqc(species, adapter_removed_reads, output_folder)
        
    print_success(f"fastqc for species {species} adapter removed data complete")

def fastqc_for_duplicates_removed_data(species: str):
    print_info(f"Running fastqc for species {species} duplicates removed data")

    duplicates_removed_reads_folder = get_folder_path_species_processed_duplicates_removed(species)
    output_folder = get_folder_path_species_results_qc_fastqc_duplicates_removed(species)

    duplicates_removed_reads = get_files_in_folder_matching_pattern(duplicates_removed_reads_folder, f"*{FILE_ENDING_DUPLICATES_REMOVED_FASTQ_GZ}")

    files_list = get_files_in_folder_matching_pattern(output_folder, f"*{FILE_ENDING_FASTQC_HTML}")

    if len(files_list) > 0:
        print_info(f"Fastqc for duplicates removed already exists for species {species}. Skipping.")
        return
    
    if len(duplicates_removed_reads) == 0:
        print_warning(f"No duplicate removed reads found for species {species}. Skipping.")
        return
    
    execute_fastqc(species, duplicates_removed_reads, output_folder)

    print_success(f"fastqc for species {species} duplicates removed data complete")

def execute_fastqc(species: str, reads_file_list: list, output_folder: str):

    if len(reads_file_list) == 0:
        raise Exception(f"No reads provided.")

    print_info(f"Running fastqc for {len(reads_file_list)} files for species {species}")

    threads = get_threads_count_for_fastqc()

    command = f"{PROGRAM_PATH_FASTQC} -o {output_folder} -t {threads} {' '.join(reads_file_list)}"
    try:
        subprocess.run(command, shell=True, check=True)
        print_success(f"Fastqc for species {species} complete")
    except Exception as e:
        print_error(f"Failed to run fastqc for species {species}: {e}")

def all_species_fastqc():

    print_execution("Running fastqc for all species before and after adapter removal")

    for species in FOLDER_SPECIES: 
        fastqc_for_species(species)

    print_info("Fastqc for all species before and after adapter removal completed successfully.")

def all_species_fastqc_raw():
    print_execution("Running fastqc for all species raw data")

    for species in FOLDER_SPECIES: 
        fastqc_for_raw_data(species)

    print_info("Fastqc for all species raw data completed successfully.")

def all_species_fastqc_adapter_removed():
    print_execution("Running fastqc for all species trimmed data")

    for species in FOLDER_SPECIES: 
       fastqc_for_adapter_removed_data(species)

    print_info("Fastqc for all species trimmed data completed successfully.")

def all_species_fastqc_quality_filtered():
    print_execution("Running fastqc for all species quality filtered data")

    for species in FOLDER_SPECIES: 
        fastqc_for_quality_filtered_data(species)

    print_info("Fastqc for all species quality filtered data completed successfully.")

def all_species_fastqc_duplicates_removed():
    print_execution("Running fastqc for all species duplicates removed data")

    for species in FOLDER_SPECIES: 
        fastqc_for_duplicates_removed_data(species)

    print_info("Fastqc for all species duplicates removed data completed successfully.")


def main():
    all_species_fastqc()

if __name__ == "__main__":
    main()
