import os
import json
from prefect_gcp import GcpCredentials
from prefect.filesystems import GCS


gcp_credentials = GcpCredentials.load("gcp-creds")

bucket_name = os.environ['GCP_BUCKET_NAME']

cloud_storage = GCS(
    bucket_path=bucket_name,
    service_account_info=json.dumps(gcp_credentials.service_account_info.get_secret_value()),
)
cloud_storage.save("spotify-gcs", overwrite=True)
