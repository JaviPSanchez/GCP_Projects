# Input Variables
variable "project_id" {
  description = "Project config "
  type = string
}

variable "region" {
    description = "Region of the project"
    type = string
}

variable "ssh_source_range" {
  description = "Allowed SSH source IPs"
  type        = list(string)
}

variable "ssh_port" {
  description = "Allowed SSH port"
  type        = list(string)
}

variable "http_source_range" {
  description = "Allowed HTTP source IPs"
  type        = list(string)
}

