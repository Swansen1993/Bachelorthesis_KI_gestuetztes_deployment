variable "environment_name" {
  description = "name der umgebung (low,medium,high,extreme)"
  type        = string
}

variable "vpc_cidr" {
  description = "CIDR-block der isolierten VPC"
  type        = string
}

variable "app_cpu" {
  description = "Hardwareresourcen CPU für den Applikations Container"
  type        = string
}

variable "app_memory" {
  description = "Speicher für den Applikations Container"
  type        = string
}

variable "test_cpu" {
  description = "Cpu Ressourcen für den Test Container (Runner)"
  type        = string
}

variable "test_memory" {
  description = "Memory Ressourcen für den Test Container (Runner)"
  type        = string
}

variable "app_image_uri" {
  description = "URI des Images der App (Code)"
  type        = string
}

variable "locust_image_uri" {
  description = "URI des images des locust lasttst runner"
  type        = string
}


variable "locust_test_user_count" {
  description = "Anzahl der simmulierten user"
  type        = number
  default     = 5
}

variable "locust_spawn_rate" {
  description = "Hinzuschalten neuer user"
  type        = number
  default     = 1
}

variable "locust_test_runtime" {
  description = "Wie lange läuft der Test?"
  type        = string
  default     = "60s"
}

variable "s3_bucket_aws" {
  description = "s3 bucket für speichern der metriken in json-format"
  type        = string
}



variable "variant_id" {
  description = "ID des untersuchten Code-Beispiels (z. B. v1 bis v160)"
  type        = string
  default     = "v1"
}

variable "target_method" {
  default = "pos_001_post_add_article"
  type    = string
}
