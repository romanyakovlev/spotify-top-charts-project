export $(cat .env | xargs)

terraform init
terraform plan -var="project=$GCP_PROJECT_ID"
terraform apply -var="project=$GCP_PROJECT_ID"