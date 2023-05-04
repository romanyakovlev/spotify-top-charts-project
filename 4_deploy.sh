export $(cat .env | xargs)

source spotify_project_venv/bin/activate

# create prefect blocks
python blocks/gcp_credentials.py
python blocks/gcp_big_query.py
python blocks/gcp_cloud_run_job.py
python blocks/gcp_cloud_storage.py

# deploy cloud run flow
prefect deployment build -n "Spotify Top Charts Flow" \
    -ib cloud-run-job/spotify-cloud-run-job \
    flows/etl_flow.py:etl_flow \
    -q default -a --path /app/flows
prefect deployment run "Main flow/Spotify Top Charts Flow	"
