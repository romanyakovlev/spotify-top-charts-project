import os
from prefect_gcp import GcpCredentials, CloudRunJob

gcp_credentials = GcpCredentials.load("gcp-creds")

image = f"{os.environ['GCP_REGISTRY_ADDRESS']}/prefect-flow:python3.9"

with open(".env", 'r') as file:
    envs_list = [env for env in file.read().split("\n") if '=' in env]

environment_dict = dict([env.split('=') for env in envs_list])

cloud_run_job = CloudRunJob(
    image=image,
    credentials=gcp_credentials,
    region=os.environ["GCP_REGION"],
    env=environment_dict,
)
cloud_run_job.save("spotify-cloud-run-job", overwrite=True)
