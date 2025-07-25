import os
import subprocess
import glob
from typing import Optional

from common.common_constants import *
from common.common_logging import *
from common.common_config import *
from common.common_folder_functions import *

#####################
# Helpers
#####################

def is_species(species: str) -> bool:
    return species in config['species']

def get_species_name(species_id):

    if not is_species(species_id):
        raise ValueError(f"Invalid species ID: {species_id}")
   
    return config['species'][species_id]['name']


def is_sam_file_sorted(sam_file: str) -> bool:
    """
    Checks if a SAM file is sorted by coordinate.

    :param sam_file: The path to the SAM file
    :return: True if the SAM file is sorted by coordinate, False otherwise
    """
    try:
        # Check the header for sorting status
        result = subprocess.run(
            [PROGRAM_PATH_SAMTOOLS, PROGRAM_PATH_SAMTOOLS_VIEW, '-H', sam_file],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True
        )
        for line in result.stdout.splitlines():
            if line.startswith('@HD') and 'SO:coordinate' in line:
                # The SAM file is sorted by coordinate
                return True
        # The SAM file is not sorted by coordinate
        return False
    except subprocess.CalledProcessError as e:
        print_error(f"Error reading header: {e}")
        # Return False in case of an error
        return False

def is_fasta_file(file_name: str) -> bool:
    return file_name.endswith(FILE_ENDING_FNA) or file_name.endswith(FILE_ENDING_FA) or file_name.endswith(FILE_ENDING_FASTA)

def is_fasta_gz_file(file_name: str) -> bool:
    return file_name.endswith(FILE_ENDING_FNA_GZ) or file_name.endswith(FILE_ENDING_FA_GZ) or file_name.endswith(FILE_ENDING_FASTQ_GZ) 

def call_r_script(script_path: str, *args):
    if not os.path.exists(script_path):
        raise FileNotFoundError(f"R script not found: {script_path}")

    command = ["Rscript", script_path] + list(args)

    run_command(command, description=f"R script: {script_path}")

    # print_debug(f"Executing command: {' '.join(command)}")

    # result = subprocess.run(
    #     command,
    #     capture_output=True,
    #     text=True
    # )

    # # Combine stdout and stderr
    # combined_output = result.stdout + result.stderr

    # # Print line-by-line
    # for line in combined_output.splitlines():
    #     print_info(f"R script output: {line}") 

    # if result.returncode != 0:
    #     print_error(f"R script failed with exit code {result.returncode}")
    #     return

    # print_info(f"R script executed successfully: {script_path}")

def get_adapter_sequence(species: str) -> tuple[str,str]:
    """
    Get the adapter sequence for a given species. If not found, use the global adapter sequence.

    :param species: The species name
    :return: The adapter sequence for R1 and R2
    """
    # Check if the species is valid
    if not is_species(species):
        raise ValueError(f"Invalid species: {species}")
    
    # Get global defaults
    default_adapters = config['processing']['adapter_removal']['adapters']
    
   # Navigate species config safely
    species_config = config['species'].get(species, {})
    species_processing = species_config.get('processing', {})
    species_adapter_removal = species_processing.get('adapter_removal', {})
    species_adapter = species_adapter_removal.get('adapter', {})

    # Use species adapter if exists, else fall back to default
    adapter_sequence_r1 = species_adapter.get('r1', default_adapters['r1'])
    adapter_sequence_r2 = species_adapter.get('r2', default_adapters['r2'])

    if adapter_sequence_r1 is None and adapter_sequence_r2 is None:
        raise ValueError(f"Adapter sequence not found for species: {species}")

    return adapter_sequence_r1, adapter_sequence_r2

def get_filename_from_path(file_path: str) -> str:
    return os.path.basename(file_path)

def get_filename_from_path_without_extension(file_path: str) -> str:
    return os.path.splitext(get_filename_from_path(file_path))[0]

def get_r_script(r_script_name: str, processing_folder: str) -> str:
    r_script_path = os.path.join(get_folder_path_scripts_plots(processing_folder), r_script_name)

    if not os.path.exists(r_script_path):
        raise Exception(f"Invalid R script: {r_script_path}")   
    
    return r_script_path

def get_raw_reads_list_of_species(species: str) -> list:
     
    if not is_species_folder(species):
        raise Exception(f"Invalid species folder: {species}")
    
    raw_reads_folder = get_folder_path_species_raw_reads(species)

    return get_files_in_folder_matching_pattern(raw_reads_folder, f"*{FILE_ENDING_FASTQ_GZ}")
   

def get_files_in_folder_matching_pattern(folder: str, pattern: str) -> list:
     
    if not os.path.exists(folder):
        raise Exception(f"Invalid folder: {folder}")
    
    #read all reads from folder into list
    files = glob.glob(os.path.join(folder, pattern))

    return files

def get_raw_paired_reads_list_of_species(species: str) -> list:

    if not is_species_folder(species):
        raise Exception(f"Invalid species folder: {species}")

    folder_path = get_folder_path_species_raw_reads(species)

    find_command = f'find {folder_path} -type f \\( -name "{FILE_PATTERN_R1_FASTQ_GZ}" -o -name "{FILE_PATTERN_R2_FASTQ_GZ}" \\) ! -path "{FILE_PATTERN_UNDETERMINED_FOLDER}"'
    
    # Sort the list of files by sample ID
    sort_command = 'sort'
    
    # Use awk to format the list of files as a comma-separated list
    awk_command = 'awk \'NR%2{printf "%s,", $0} NR%2==0{print $0}\''
    
    # Combine the commands into a single command string
    full_command = f'{find_command} | {sort_command} | {awk_command}'

    print_debug(f"Running command: {full_command}")
    
    try:
        #print_info(f"Running command: {full_command}")
        command_result = subprocess.run(full_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)

    except subprocess.CalledProcessError as e:
        raise Exception(f"An error occurred while running the command: {e}")
        
    #convert output into list of files
    lines = command_result.stdout.splitlines()

    # Split each line by the comma, strip the paths to remove any extra spaces or newlines, and make them absolute paths
    file_paths = [
        [os.path.abspath(os.path.join(folder_path, paths[0].strip())),
        os.path.abspath(os.path.join(folder_path, paths[1].strip()))]
        for line in lines
        for paths in [line.strip().split(',')]  # Split the line by the comma
    ]

    return file_paths

def run_command(command: list, description: str = "", cwd: Optional[str] = None, throw_error: bool = False) -> str:
    """
    Run a shell command and return its stdout output.

    Parameters:
        command (list): The command and arguments to execute.
        description (str): Optional description for logging.
        cwd (str, optional): Working directory to execute the command in.

    Returns:
        str: Captured stdout output.

    Raises:
        subprocess.CalledProcessError: If the command fails.
    """
    print_debug("Entering run_command function")

    command_program = command[0] if command else "Unknown"

    print_info(f"Running: {description or ' '.join(command)}")
    
    if cwd:
        print_debug(f"Working directory: {cwd}")

    result = subprocess.run(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=True,
        cwd=cwd
    )

    if result.stdout:
        for line in result.stdout.splitlines():
            print_info(f"[{command_program}] {line.strip()}")

    if result.stderr and throw_error:
        print_error(f"[{command_program}] Command failed with error:")
        
        for line in result.stderr.splitlines():
            print_error(f"[{command_program}] {line.strip()}")
        
        raise subprocess.CalledProcessError(result.returncode, command, output=result.stdout, stderr=result.stderr)

    if result.stderr:
        for line in result.stdout.splitlines():
            print_warning(f"[{command_program}] {line.strip()}")

    print_info(f"{command_program} completed successfully")
    return result.stdout.strip()
