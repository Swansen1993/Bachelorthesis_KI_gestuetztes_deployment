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
  type = string
}

variable "variant_id" {
  type    = string
  default = "v1"
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
