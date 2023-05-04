import re
import os

from prefect import task, flow
from prefect.filesystems import GCS
from prefect_gcp import GcpCredentials
from google.cloud import dataproc_v1, storage


gcs_block = GCS.load("spotify-gcs")
gcp_credentials_block = GcpCredentials.load("gcp-creds")


@task
def submit_dataproc_job(region: str, cluster_name: str, spark_filename: str) -> None:
    # Create the job client.
    job_client = dataproc_v1.JobControllerClient(
        client_options={"api_endpoint": "{}-dataproc.googleapis.com:443".format(region)},
        credentials=gcp_credentials_block.get_credentials_from_service_account(),
    )
    # Create the job config.
    job = {
        "placement": {"cluster_name": cluster_name},
        "pyspark_job": {
            "main_python_file_uri": "gs://{}/{}".format(gcs_block.bucket_path, spark_filename),
            "jar_file_uris": ("gs://spark-lib/bigquery/spark-bigquery-latest_2.12.jar",),
            "args": [f"--project_id={gcp_credentials_block.project}"],
        },
    }
    operation = job_client.submit_job_as_operation(
        request={"project_id": gcp_credentials_block.project, "region": region, "job": job}
    )
    response = operation.result()
    matches = re.match("gs://(.*?)/(.*)", response.driver_output_resource_uri)
    output = (
        storage.Client(credentials=gcp_credentials_block.get_credentials_from_service_account())
        .get_bucket(matches.group(1))
        .blob(f"{matches.group(2)}.000000000")
        .download_as_string()
    )
    print(f"Job finished successfully: {output}\r\n")


@task
def upload_pyspark_jobs_to_gcs(local_path: str = "pyspark_jobs", to_path: str = "jobs") -> None:
    gcs_block.put_directory(local_path=local_path, to_path=to_path)


@flow(log_prints=True, name="Subflow - Data Transformation step")
def etl_transform_data():
    cluster_name = os.environ["GCP_CLUSTER_NAME"]
    region = os.environ["GCP_REGION"]
    spark_filename = "jobs/pyspark_job.py"
    pyspark_local_path = "pyspark_jobs"
    pyspark_gcs_path = "jobs"
    upload_pyspark_jobs_to_gcs(pyspark_local_path, pyspark_gcs_path)
    submit_dataproc_job(region, cluster_name, spark_filename)


if __name__ == "__main__":
    etl_transform_data()
