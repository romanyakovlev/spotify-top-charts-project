terraform {
  required_version = ">= 1.0"
  backend "local" {}  # Can change from "local" to "gcs" (for google) or "s3" (for aws), if you would like to preserve your tf-state online
  required_providers {
    google = {
      source  = "hashicorp/google"
    }
  }
}

provider "google" {
  project = var.project
  region = var.region
}

# Data Lake Bucket
resource "google_storage_bucket" "data-lake-bucket" {
  name          = "${local.data_lake_bucket}_${var.project}"
  location      = var.region

  # Optional, but recommended settings:
  storage_class = var.storage_class
  uniform_bucket_level_access = true

  versioning {
    enabled     = true
  }

  lifecycle_rule {
    action {
      type = "Delete"
    }
    condition {
      age = 30  // days
    }
  }

  force_destroy = true
}

# DWH
resource "google_bigquery_dataset" "dataset" {
  dataset_id = var.BQ_DATASET
  project    = var.project
  location   = var.region
}

# Dataproc cluster
resource "google_dataproc_cluster" "simplecluster" {
  name   = "${local.cluster}-${var.project}"
  region = var.region
}

# Artifact Registry
resource "google_artifact_registry_repository" "agent-repo" {
  location      = var.region
  repository_id = "spotify"
  description   = "spotify docker repository"
  format        = "DOCKER"
}

# Compute Engine VM Instance
resource "google_compute_instance" "default" {
  name         = "prefect-agent"
  machine_type = "e2-medium"
  zone         = var.region

  tags = ["http-server", "https-server"]

  boot_disk {
    initialize_params {
      image = "debian-cloud/debian-11"
    }
  }

  network_interface {
    network = "default"
  }

  # set ssh port to 80
  metadata_startup_script = "echo \"Port 80\" > /etc/ssh/sshd_config; sudo systemctl reload sshd.service"

}