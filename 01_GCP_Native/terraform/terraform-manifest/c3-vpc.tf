# Resource Block: VPC
resource "google_compute_network" "myvpc" {
  name = "coin-vm"
  auto_create_subnetworks = false   
}

# Resource Block: Subnet
resource "google_compute_subnetwork" "mysubnet" {
  name = "coin-vm-subnet"
  region = "us-central1"
  ip_cidr_range = "10.128.0.0/20"
  network = google_compute_network.myvpc.id 
}