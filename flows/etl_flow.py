from prefect import task, flow

from etl_web_to_gcs import etl_web_to_gcs
from etl_gcs_to_bq import etl_gcs_to_bq
from etl_transform_data import etl_transform_data


@flow(name="Main flow", log_prints=True)
def etl_flow():
    """Main ETL flow"""
    etl_web_to_gcs()
    etl_gcs_to_bq()
    etl_transform_data()


if __name__ == "__main__":
    etl_flow()
