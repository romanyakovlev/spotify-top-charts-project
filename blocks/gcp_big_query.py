from prefect_gcp.bigquery import BigQueryWarehouse
from prefect_gcp import GcpCredentials


gcp_credentials = GcpCredentials.load("gcp-creds")

bigquery_warehouse_block = BigQueryWarehouse(gcp_credentials=gcp_credentials)
bigquery_warehouse_block.save("zoom-bigquery", overwrite=True)
