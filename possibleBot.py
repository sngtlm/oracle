import oci
from time import ctime, sleep
from random import sample

# Create a default config using DEFAULT profile in default location
# Refer to
# https://docs.cloud.oracle.com/en-us/iaas/Content/API/Concepts/sdkconfig.htm#SDK_and_CLI_Configuration_File
# for more info
config = oci.config.from_file()

ssh_authorized_keys = "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQCngj8ZPlFq1lZJJxB9bQcSAIsjtZyamncB5v1VZ/DyVoce0SJvXVFNm1LN4a7UaLuvzzTuNnAXeu1jYsaFQuKHLKHexfoVG9V6pyw2gitOjGmOgvIdt0aWPLxRA2DRdrZ3Mpw7ioCsQ0gMmB5tFDOe2a7/Iw1Rapwrk8n5wDmqeOxaE9TX6/ter5IW+GQJDjx6YJwGFvAoU4cqACdkXRiU4qTAkcfkB8cwNiivd5RzXXS8faExGqCdCTHy1MtkyzD/wAhsWYO0Dnhx+FcieuJH6dLHXA3cFcYoW5Z1MXFxZ5xDDdse22tgDGt/l8Mx0Dmjel7NLNcozz7k/yoQ3iXT ssh-key-2023-02-07"


# Initialize service client with default config file
core_client = oci.core.ComputeClient(config)
vnic=oci.core.models.CreateVnicDetails(
   subnet_id='ocid1.subnet.oc1.phx.aaaaaaaahsobsvekg2kgllfgxc7zqb6avbar4vbacggodrkewblq6ubet5ra')
sc=oci.core.models.LaunchInstanceShapeConfigDetails( ocpus=CORES, memory_in_gbs=MEM)

def f(ad):
 return oci.core.models.LaunchInstanceDetails(
   availability_domain=ad,
   compartment_id='ocid1.tenancy.oc1..aaaaaaaa4d5h26osxmonwduti7gcaqvwciwogizsxznyuw76qgwhaz5jwboa',
   shape='VM.Standard.A1.Flex',
   create_vnic_details=vnic,
   display_name='minecraftServer',
   metadata={"ssh_authorized_keys": ssh_authorized_keys },
   image_id='ocid1.image.oc1.phx.aaaaaaaaxfzn7tzdjnxzhal4uhqt57rvz3ypndgrlrlpcgpgnslsq7coxkka',
   shape_config=sc) 

created=False

ads = ['kLlY:PHX-AD-1', 'kLlY:PHX-AD-2', 'kLlY:PHX-AD-2']

print('Starting launch process: ' + ctime())
while created == False:
   try:
       launch_instance_response = core_client.launch_instance(f(sample(ads, 1)[0]))
       created = True
   except Exception as exc:
      print(exc)
      sleep(10)
      print('Retrying') 
  
print('Launch process complete: ' + ctime())
