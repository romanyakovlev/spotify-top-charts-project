import os
from prefect_gcp import GcpCredentials

project_name = os.environ['GCP_PROJECT_ID']

with open(os.environ['GOOGLE_APPLICATION_CREDENTIALS'], 'r') as file:
    service_account_info = file.read()

gcp_credentials = GcpCredentials(
    service_account_info=service_account_info,
    project=project_name
)
gcp_credentials.save("gcp-creds", overwrite=True)
