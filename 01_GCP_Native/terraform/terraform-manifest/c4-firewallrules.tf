# Resource Block: Firewall Rule: SSH
resource "google_compute_firewall" "fw_ssh" {
  name = "fwrule-allow-ssh22"
  allow {
    ports    = var.ssh_port
    protocol = "tcp"
  }
  direction     = "INGRESS"
  network       = google_compute_network.myvpc.id 
  priority      = 1000
  source_ranges = var.ssh_source_range
  target_tags   = ["ssh-tag"]
}

# Resource Block: Firewall Rule: HTTP Port
resource "google_compute_firewall" "fw_http" {
  name = "fwrule-allow-http80"
  allow {
    ports    = ["80"]
    protocol = "tcp"
  }
  direction     = "INGRESS"
  network       = google_compute_network.myvpc.id 
  priority      = 1000
  source_ranges = var.http_source_range
  target_tags   = ["webserver-tag"]
}
