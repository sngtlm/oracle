displayName = 'minecraftServer'
compartmentId = 'ocid1.tenancy.oc1..aaaaaaaa4d5h26osxmonwduti7gcaqvwciwogizsxznyuw76qgwhaz5jwboa'
availabilityDomain = "kLlY:PHX-AD-1"
imageId = "ocid1.image.oc1.phx.aaaaaaaaxfzn7tzdjnxzhal4uhqt57rvz3ypndgrlrlpcgpgnslsq7coxkka"
subnetId = 'ocid1.subnet.oc1.phx.aaaaaaaahsobsvekg2kgllfgxc7zqb6avbar4vbacggodrkewblq6ubet5ra'
ssh_authorized_keys = "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQCngj8ZPlFq1lZJJxB9bQcSAIsjtZyamncB5v1VZ/DyVoce0SJvXVFNm1LN4a7UaLuvzzTuNnAXeu1jYsaFQuKHLKHexfoVG9V6pyw2gitOjGmOgvIdt0aWPLxRA2DRdrZ3Mpw7ioCsQ0gMmB5tFDOe2a7/Iw1Rapwrk8n5wDmqeOxaE9TX6/ter5IW+GQJDjx6YJwGFvAoU4cqACdkXRiU4qTAkcfkB8cwNiivd5RzXXS8faExGqCdCTHy1MtkyzD/wAhsWYO0Dnhx+FcieuJH6dLHXA3cFcYoW5Z1MXFxZ5xDDdse22tgDGt/l8Mx0Dmjel7NLNcozz7k/yoQ3iXT ssh-key-2023-02-07"

import os
os.system("pip install oci")
os.system("pip install requests")
import oci
import logging
import time
import sys
import requests

LOG_FORMAT = '[%(levelname)s] %(asctime)s - %(message)s'
logging.basicConfig(
    level=logging.INFO,
    format=LOG_FORMAT,
    handlers=[
        logging.FileHandler("oci.log"),
        logging.StreamHandler(sys.stdout)
    ]
)

ocpus = 4
memory_in_gbs = 24
wait_s_for_retry = 10

logging.info("#####################################################")
logging.info("Script to spawn VM.Standard.A1.Flex instance")


message = f'Start spawning instance VM.Standard.A1.Flex - {ocpus} ocpus - {memory_in_gbs} GB'
logging.info(message)

logging.info("Loading OCI config")
config = oci.config.from_file(file_location="./config")

logging.info("Initialize service client with default config file")
to_launch_instance = oci.core.ComputeClient(config)


message = f"Instance to create: VM.Standard.A1.Flex - {ocpus} ocpus - {memory_in_gbs} GB"
logging.info(message)

logging.info("Check current instances in account")
logging.info(
    "Note: Free upto 4xVM.Standard.A1.Flex instance, total of 4 ocpus and 24 GB of memory")
current_instance = to_launch_instance.list_instances(
    compartment_id=compartmentId)
response = current_instance.data

total_ocpus = total_memory = _A1_Flex = 0
instance_names = []
if response:
    logging.info(f"{len(response)} instance(s) found!")
    for instance in response:
        logging.info(f"{instance.display_name} - {instance.shape} - {int(instance.shape_config.ocpus)} ocpu(s) - {instance.shape_config.memory_in_gbs} GB(s) | State: {instance.lifecycle_state}")
        instance_names.append(instance.display_name)
        if instance.shape == "VM.Standard.A1.Flex" and instance.lifecycle_state not in ("TERMINATING", "TERMINATED"):
            _A1_Flex += 1
            total_ocpus += int(instance.shape_config.ocpus)
            total_memory += int(instance.shape_config.memory_in_gbs)

    message = f"Current: {_A1_Flex} active VM.Standard.A1.Flex instance(s) (including RUNNING OR STOPPED)"
    logging.info(message)
else:
    logging.info(f"No instance(s) found!")


message = f"Total ocpus: {total_ocpus} - Total memory: {total_memory} (GB) || Free {4-total_ocpus} ocpus - Free memory: {24-total_memory} (GB)"
logging.info(message)

if total_ocpus + ocpus > 4 or total_memory + memory_in_gbs > 24:
    message = "Total maximum resource exceed free tier limit (Over 4 ocpus/24GB total). **SCRIPT STOPPED**"
    logging.critical(message)
    sys.exit()

if displayName in instance_names:
    message = f"Duplicate display name: >>>{displayName}<<< Change this! **SCRIPT STOPPED**"
    logging.critical(message)
    sys.exit()

message = f"Precheck pass! Create new instance VM.Standard.A1.Flex: {ocpus} opus - {memory_in_gbs} GB"
logging.info(message)

instance_detail = oci.core.models.LaunchInstanceDetails(
    metadata={
        "ssh_authorized_keys": ssh_authorized_keys
    },
    availability_domain=availabilityDomain,
    shape='VM.Standard.A1.Flex',
    compartment_id=compartmentId,
    display_name=displayName,
    source_details=oci.core.models.InstanceSourceViaImageDetails(
        source_type="image", image_id=imageId),
    create_vnic_details=oci.core.models.CreateVnicDetails(
        assign_public_ip=False, subnet_id=subnetId, assign_private_dns_record=True),
    agent_config=oci.core.models.LaunchInstanceAgentConfigDetails(
        is_monitoring_disabled=False,
        is_management_disabled=False,
        plugins_config=[oci.core.models.InstanceAgentPluginConfigDetails(
            name='Vulnerability Scanning', desired_state='DISABLED'), oci.core.models.InstanceAgentPluginConfigDetails(name='Compute Instance Monitoring', desired_state='ENABLED'), oci.core.models.InstanceAgentPluginConfigDetails(name='Bastion', desired_state='DISABLED')]
    ),
    defined_tags={},
    freeform_tags={},
    instance_options=oci.core.models.InstanceOptions(
        are_legacy_imds_endpoints_disabled=False),
    availability_config=oci.core.models.LaunchInstanceAvailabilityConfigDetails(
        recovery_action="RESTORE_INSTANCE"),
    shape_config=oci.core.models.LaunchInstanceShapeConfigDetails(
        ocpus=ocpus, memory_in_gbs=memory_in_gbs)
)

to_try = True
while to_try:
    try:
        to_launch_instance.launch_instance(instance_detail)
        to_try = False
        message = 'Success! Edit vnic to get public ip address'
        logging.info(message)
        sys.exit()
    except oci.exceptions.ServiceError as e:
        if e.status == 500:
            message = f"{e.message} Retry in {wait_s_for_retry}s"
        else:
            message = f"{e} Retry in {wait_s_for_retry}s"
        logging.info(message)
        time.sleep(wait_s_for_retry)
    except Exception as e:
        message = f"{e} Retry in {wait_s_for_retry}s"
        logging.info(message)
        time.sleep(wait_s_for_retry)
    except KeyboardInterrupt:
        sys.exit()
