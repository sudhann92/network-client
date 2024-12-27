'''
# Updated Code to Address ModuleNotFoundError
# Added condition to check if 'jnpr' library is available and fallback logic for testing without it.
# This script useage juniper device
   #1. Copy the UAC tar file to master router and Backup router
   #2. un tar the UAC file in master
   #3. switch to root user in master router and run the UAC command to capture log file
   #4. Once the command completed Jump to backup router follow the step 2 and step 3
   #5. copy the log tar file to master router and deleted the files in backup router to cleaned up the files
   #6. Once copied to master then copied the both files back to Jump server and deleted the UAC files and folders in master
# Created Function below to perfom the above steps
  #secure_copy_file,determine_re_roles,execute_uac_commands_master,execute_uac_commands_backup,
  #pull_out_tar_log_data,delete_file_master_RE,process_device,main
# Input User should provide "host file.txt",Router user name,Router password,Root password, UAC tar file path
'''
import os
import sys
import getpass
import re
import time
from datetime import datetime
import csv

try:
    from jnpr.junos import Device
    from jnpr.junos.utils.scp import SCP
    from jnpr.junos.utils.fs import FS
    from jnpr.junos.utils.start_shell import StartShell
    from jnpr.junos.exception import ConnectError, RpcError, ConnectAuthError,CommitError
    from jnpr.junos.utils.config import Config
    JNPR_AVAILABLE = True
except ModuleNotFoundError:
    print("ERROR: The 'jnpr' library is not installed. Ensure it is available in your environment.")
    JNPR_AVAILABLE = False



class RootPasswordError(Exception):
    """Raised when the root password is incorrect."""
    pass


def secure_copy_file(dev, local_path, remote_path):
    '''Copy file securely to the device using scp module'''
    if not JNPR_AVAILABLE:
        raise RuntimeError("'jnpr' library is unavailable.")
    try:
        with SCP(dev) as scp:
            scp.put(local_path, remote_path)
        print(f"File copied to device: {remote_path}")
    except Exception as e:
        print(f"Failed to copy file: {e}")


def determine_re_roles(device):
    '''Find the master and backup RE name'''
    if not JNPR_AVAILABLE:
        raise RuntimeError("'jnpr' library is unavailable.")
    try:
        #RPC to pull info as JSON format and manipulated the data for get the master and backup slot number
        result = device.rpc.get_route_engine_information({'format':'json'})
        re_info = result["route-engine-information"][0]["route-engine"]
        master_re, backup_re = None, None
        for re in re_info :
            slot = re['slot'][0]['data']
            state = re['mastership-state'][0]['data']
            if state == 'master':
                master_re = slot
            else:
                backup_re = slot
        print(f"Master:{master_re} Backup:{backup_re}")
        return master_re, backup_re
    except RpcError as e:
        print(f"Error determining master/backup RE: {e}")
        return None, None


def execute_uac_commands_master(dev,root_password):
        '''Used to run in master Router'''
        if not JNPR_AVAILABLE:
          raise RuntimeError("'jnpr' library is unavailable.")
        try:
            with StartShell(dev) as sh:
                sh.run('su',this='Password:',sleep=2)
                root_password_output_master = sh.run(root_password,this='(#|%)\\s',sleep=3)
                root_console = sh.run("whoami", this="root")
                #Check the root@ string in root_password_output_master variable then it will proceed remaining steps
                if re.search(r"root", root_console[1]):
                        print("Entered root console sucessfully")
                        sh.run(f'tar zxf {REMOTE_FILE_PATH}{NAME_OF_TAR_PACKAGE}', this='#', sleep=2)
                        print("Unzipped the file successfully")
                        start_master = time.time()
                        uac_command_output = sh.run(f'cd {FOLDER_NAME} && {UAC_COMMANDS} && echo "DONE"', this='DONE', timeout=700, sleep=5)
                        print(f"CD and UAC command backup: {time.time() - start_master} seconds")
                        #print(f"uac_command_output")
                        #Again used th regex search for the DONE string from uac command output then proceed further
                        if re.search(r"^\s*DONE\s*$",uac_command_output[1], re.MULTILINE):
                        #uac_command_output[0] and "DONE" == uac_command_output[1].splitlines()[-1]:
                            path_val = sh.run(f'grep -iw "output file created" {REMOTE_FILE_PATH}uac_output.log', this='Output', timeout=30, sleep=2)
                            pattern=r"/var/tmp/.*?\.tar\.gz"
                            match = re.search(pattern, path_val[1])
                            if match:
                                tar_gz_full_path = match.group(0)
                                print(f"Log generated sucessfully in master:{tar_gz_full_path}")
                            else:
                               print(f'ERROR: File not generated properly check the uac_output.log inside in Master router')
                        else:
                            print(f"ERROR: UAC Command Not run properly {uac_command_output}")
                else:
                    print(f'ERROR: root password is worng in Master re {root_password_output_master}')
                    raise RootPasswordError("Incorrect root password")
                    # sh.run('exit', this="exit", sleep=2)
                    # tar_gz_full_path=changing_root_password_failed(dev)
                sh.run('exit', this="exit", sleep=2)
            return tar_gz_full_path
        except RootPasswordError as e:
           print(f"ERROR: {e}")
           raise
        except Exception as e:
           print(f"ERROR: executing commands: {e}")


def changing_root_password_failed(dev):
    try:
        tar_gz_full_path  = None
        set_root_password ='''set system root-authentication encrypted-password "$1$a/AOqmNS$0yK5sWW1"'''
        with Config(dev, mode="exclusive") as cu:
            updated_new_password=cu.load(set_root_password, format="set")
            print(f"Updated the Password in this device{updated_new_password}")
            commiting_pass = cu.commit()
            print(f"password output result: {commiting_pass}")
        tar_gz_full_path = execute_uac_commands_master(dev,ROOT_PASSWORD)
    except CommitError as com:
        print(f"The Set password command not Updated in the device please check manually {com} {updated_new_password}")
    except Exception as e:
          print(f"An error occurred: {e}")
    return tar_gz_full_path


def execute_uac_commands_backup(dev, root_password, master_router):
    '''Run the UAC command in Backup Router'''
    if not JNPR_AVAILABLE:
        raise RuntimeError("'jnpr' library is unavailable.")
    try:
        with StartShell(dev) as sh:
            backup_router_command=sh.run('cli -c "request routing-engine login other-routing-engine"',">")
            print('Entered into backup re')
            if re.search(r"backup", backup_router_command[1]):
                sh.run("start shell user root",this='Password:', sleep=2)
                root_password_output=sh.run(root_password, this='(#|%)\\s',sleep=2)
                root_console = sh.run("whoami", this="root")
                if re.search(r"root", root_console[1]):
                    start = time.time()
                    sh.run(f'tar zxf {REMOTE_FILE_PATH}{NAME_OF_TAR_PACKAGE}', this='#', sleep=2)
                    print("Unzipped the file successfully")
                    uac_command_output_backup = sh.run(f'cd {FOLDER_NAME} && {UAC_COMMANDS} && echo "DONE"', this='DONE', timeout=700, sleep=5)
                    print(f"CD and UAC command backup: {time.time() - start} seconds")
                    #start = time.time()
                    if re.search(r"^\s*DONE\s*$",uac_command_output_backup[1], re.MULTILINE):
                    #uac_command_output[0] and "DONE" == uac_command_output[1].splitlines()[-1]:
                        path_val = sh.run(f'grep -iw "output file created" {REMOTE_FILE_PATH}uac_output.log', this='Output', timeout=20, sleep=2)
                        #print(path_val)
                        pattern=r"/var/tmp/.*?\.tar\.gz"
                        match = re.search(pattern, path_val[1])
                        if match:
                            tar_gz_full_path = match.group(0)
                            tar_file_name = os.path.basename(match.group(0))
                            copied_to_master=sh.run(f"cli -c 'file copy {tar_gz_full_path} re{master_router}:{REMOTE_FILE_PATH}Backup-{tar_file_name}'",this="#", sleep=1)
                            print(f"Copied to Master Router Successfully")
                            if copied_to_master[0]:
                                sh.run(f'rm -rf {REMOTE_FILE_PATH}uac-*-netbsd-* && rm -rf /var/home/superuser/{FOLDER_NAME}', this='#')
                                print("cleaned up the tar and UAC directory in back up RE")
                        else:
                         print(f'ERROR: File not genereated properly check the uac_output.log inside in backup router')
                    else:
                            print(f"ERROR: UAC Command Not run properly {uac_command_output_backup}")
                else:
                    print(f'ERROR: root password is worng in backup re {root_password_output}')
            else:
                print(f"ERROR: Problem in login to the back router or no backup router available")
            # print(output)
            sh.run('exit', this="exit", sleep=0)
        return tar_file_name
    except Exception as e:
        print(f"ERROR executing commands: {e}")

def pull_out_tar_log_data(dev,file_list):
    '''Copy file securely back to Jump host from Master device'''
    if not JNPR_AVAILABLE:
        raise RuntimeError("'jnpr' library is unavailable.")
    try:
        _file_count=0
        with SCP(dev, progress=True) as scp:
            for tar_name in file_list:
              scp.get(f"{REMOTE_FILE_PATH}{tar_name}", LOCAL_PATH)
              print(f"File transfer successful: {LOCAL_PATH}{tar_name}")
              _file_count+=1
        return "File copied successfully",_file_count
    except Exception as e:
        print(f"Error: Failed to copy file: {e}")
        return None

def delete_file_master_RE(dev, root_password):
    try:
        with StartShell(dev) as sh:
                sh.run('su',this='Password:',sleep=2)
                root_password_output_master = sh.run(root_password,this='#',sleep=2)
                root_console = sh.run("whoami", this="root")
                if re.search(r"root", root_console[1]):
                        sh.run(f'rm -rf {REMOTE_FILE_PATH}Backup-uac-* {REMOTE_FILE_PATH}uac-*-netbsd-* /var/home/superuser/{FOLDER_NAME}', this='#')
                        print("Cleaned up the tar and UAC directory in Master up RE")
    except Exception as e:
           print(f"ERROR executing commands: {e}{root_password_output_master}")


def process_device(host,number_of_router):
    if not JNPR_AVAILABLE:
        print("'jnpr' library is unavailable. Skipping device processing.")
        return
    try:
        print("\n"+"-" * 80)
        print(f"*************{number_of_router}:LOGGING TO THE MASTER {host} RE.*****************")
        print("-" * 80 +"\n")
        master_file_name=''
        Backup_file_name=''
        #Device function to connection the master router
        with Device(host=host, user=USER_NAME, passwd=PASSWORD, conn_open_timeout=500, port=22) as dev:
            if dev.connected:
                host_facts = dev.facts
                host_name = host_facts["hostname"]
                print(f"Connected to {host_name}")
                #Calling the SCP function to copy the file from Jump server to router
                secure_copy_file(dev, JUMP_HOST_FILE_PATH, REMOTE_FILE_PATH)

                #Determined the master and Backup by using the determine_re_roles functions
                master_re, backup_re = determine_re_roles(dev)
                if master_re is None or backup_re is None:
                    print(f"Could not determine master/backup RE for {host_name}")
                    sys.exit(1)

                #Used the FS utils to copy the files between the master and backup router
                fs_util = FS(dev)
                backup_path = f"re{backup_re}:{REMOTE_FILE_PATH}{NAME_OF_TAR_PACKAGE}"
                fs_util.cp(f"{REMOTE_FILE_PATH}{NAME_OF_TAR_PACKAGE}", backup_path)

                #Run the UAC command in master Node
                print("--------Executing in Master router--------")
                try:
                   master_tar_file_path= execute_uac_commands_master(dev,ROOT_PASSWORD)
                   if master_tar_file_path:
                        print(f"Master tar file path: {master_tar_file_path}")
                        root_password_updated = ""
                except RootPasswordError:
                    print("Retrying due to root password error...")
                    master_tar_file_path = changing_root_password_failed(dev)
                    if master_tar_file_path:
                        print(f"Master tar file path: {master_tar_file_path}")
                        root_password_updated = "Updated"
               # except Exception as e:
               #     print(f"ERROR: Unexpected error occurred: {e}")

                #Backup Router execution
                print("---------Executing in backup router---------")
                backup_tar_file_name=execute_uac_commands_backup(dev,ROOT_PASSWORD,master_re)
                print(f'{os.path.basename(master_tar_file_path)}, {backup_tar_file_name}')
                master_file_name = f'{os.path.basename(master_tar_file_path)}'
                Backup_file_name =f'Backup-{backup_tar_file_name}'
                print(f"Log collecting Processing for {host_name} completed.")

                 #Store the log file name for pull out it to jump server
                print("---------Pulling out & Deleting date from master router------------")
                if len(master_file_name) != 0 and len(Backup_file_name) != 0:
                    print('Pulling the data from Master router..........')
                    scp_file_name = master_file_name+'&'+Backup_file_name
                    scp_list_name = scp_file_name.split('&')
                    print(scp_list_name)
                    #Calling the pull_out_tar_log_data function for pulled the tar outside from the router
                    scp_file_value,file_count = pull_out_tar_log_data(dev,scp_list_name)
                else:
                    print("SCP Process skipped because Backup or Master generated files not available in router")

                #Delete the File and folder inside in master Router
                if scp_file_value != None:
                    delete_file_master_RE(dev,ROOT_PASSWORD)
                print(f"\n*********All Steps has been completed in this {host_name}**************")
            else:
                print(f"ERROR: Failed to connect to {host_name}")


    except ConnectAuthError as autherr:
        print(f"ERROR: Authentication error for {host_name}: {autherr}")
    except ConnectError as conn_err:
        print(f"ERROR: Connection error to device {host_name}: {conn_err}")
    except RpcError as rpc_err:
        print(f"ERROR: RPC error on device {host_name}: {rpc_err}")
    except Exception as e:
        print(f"ERROR: Unexpected error on device {host_name}: {e}")
    finally:
        #Create the completed list for Routers#
        try:
            print("capture the devicename,status for upadate in csv")
            if (file_count and file_count == 2) and (scp_list_name and len(scp_list_name) == 2):
                router_success_list=[host_name, "completed", root_password_updated]
                Device_name_status.append(router_success_list)
                print(Device_name_status)
            else:
                router_success_list=[host_name, "Failed",'']
                Device_name_status.append(router_success_list)
                print(Device_name_status)
        except NameError as e:
            router_success_list=[host_name, "Failed",'']
            Device_name_status.append(router_success_list)
            print(Device_name_status)
        print(f"\n*************Finished processing {host_name}********************")

def main():
    if not JNPR_AVAILABLE:
        print("ERROR: Script cannot proceed without 'jnpr' library. Exiting.")
        sys.exit(1)

    if not os.path.exists(LIST_OF_HOST_FILE):
        print(f"ERROR: Device file {LIST_OF_HOST_FILE} not found.")
        sys.exit(1)

    with open(LIST_OF_HOST_FILE, 'r') as read_host:
        hosts = [line.strip() for line in read_host if line.strip()]
        number_of_router = 0
        for host in hosts:
            number_of_router += 1
            process_device(host,number_of_router)
        field_name = ["Name_of_Router", "Status", "root_password_status"]
        #print(Device_name_status)
        with open(capture_output_csv, "w", newline='') as csv_file:
            csvwriter=csv.writer(csv_file)
            #write the field name in file
            csvwriter.writerow(field_name)
            #write the router row list
            csvwriter.writerows(Device_name_status)
        print("\n ROUTER STATUS DATA has been written in the csv file succesfully")

if __name__ == '__main__':

    date_time_value= datetime.now().strftime("%d-%m-%Y_%H_%M_%S")
    # Input value from User End to Run this script & #Define path and few command to run for router end


    LIST_OF_HOST_FILE= str(input("\n\033[92m 1.Enter the HOST FILE PATH: \033[00m")).strip()
    USER_NAME = str(input("\n\033[92m 2.Enter the Username for the Router: \033[00m").strip())
    PASSWORD = getpass.getpass("\n\033[92m 3.Enter the device password of Router: \033[00m").strip()
    ROOT_PASSWORD = getpass.getpass("\n\033[92m 4.Enter ROOT password for shell access for Router: \033[00m").strip()
    JUMP_HOST_FILE_PATH = str(input("\n\033[92m 5.Enter the UAC TAR FILE FULL PATH: \033[00m")).strip()
    NAME_OF_USER = str(input("\n\033[92m 2.Enter the Given Name to create the log file: \033[00m").strip())

    NAME_OF_TAR_PACKAGE = os.path.basename(JUMP_HOST_FILE_PATH).strip()
    FOLDER_NAME = NAME_OF_TAR_PACKAGE.replace('.tar.gz', '').strip()
    REMOTE_FILE_PATH = "/var/tmp/"
    LOCAL_PATH = "/infranet/uac/"
    UAC_COMMANDS = "sh uac -s netbsd -p full /var/tmp > /var/tmp/uac_output.log"
    Device_name_status =[]
    capture_output_csv=f"{NAME_OF_USER}-uac-device-log-status-{date_time_value}.csv"

    print(f"NAME OF THE LOG FILE TO CAPTURE THE SCRIPT OUTPUT : {NAME_OF_USER}-script-log-message-{date_time_value}.txt ")
    print(f"FINAL COMPLETED ROUTER LIST IN :{NAME_OF_USER}-uac-device-log-status-{date_time_value}.csv")
    try:
        with open(f'{NAME_OF_USER}-script-log-message-{date_time_value}.txt', "a", buffering=1) as log:
            sys.stdout = log
            date_time_value= datetime.now().strftime("%d-%m-%Y_%H_%M_%S")
            print(f"\n+++++++++++++++START TIME OF THE SCRIPT {datetime.now()}++++++++++++++")
            main()
            print(f"\n++++++++++++++++END TIME OF THE SCRIPT {datetime.now()}++++++++++++++++")
    finally:
        sys.stdout = sys.__stdout__
