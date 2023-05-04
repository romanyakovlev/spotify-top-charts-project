export $(cat .env | xargs)

# push image to registry
docker build -f etc/Dockerfile -t $GCP_REGISTRY_ADDRESS/prefect-flow:python3.9 .
docker push $GCP_REGISTRY_ADDRESS/prefect-flow:python3.9