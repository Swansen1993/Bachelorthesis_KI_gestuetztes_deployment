variable "aws_region" {
  type    = string
  default = "eu-central-1"
}

variable "app_image_uri" {
  type = string
}

variable "locust_image_uri" {
  type = string
}

variable "s3_bucket_aws" {
  type    = string
  default = "kpi-save-bucket-415221799955-eu-central-1-an"
}

variable "variant_id" {
  type    = string
  default = "P01"
}

variable "target_method" {
  type        = string
  default     = "pos_001_post_add_article"
  description = "name der methode die durch den Lasttest getestet wird"
}

variable "jwt_secret_key" {
  type      = string
  sensitive = true
}

variable "db_username" {
  type = string
}

variable "db_name" {
  type = string
}

variable "environments" {
  type = map(object({
    vpc_cidr               = string
    app_memory             = string
    app_cpu                = string
    test_cpu               = string
    test_memory            = string
    locust_test_user_count = number
    locust_spawn_rate      = number
    locust_test_runtime    = string
  }))
  description = "Map für die Werte der Umgebungen"
}
