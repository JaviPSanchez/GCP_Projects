# Terraform Block: Settings
terraform {
  required_version = "~> 1.9.6"
  required_providers {
    google = {
      source = "hashicorp/google"
      version = "~> 6.6.0"
    }
  }

  # backend "gcs" {
  #   bucket = "value"
  #   prefix = "terraform/state"
  # }
}

# Terraform Block: Provider
provider "google" {
  project = var.project_id
  region = var.region
}
