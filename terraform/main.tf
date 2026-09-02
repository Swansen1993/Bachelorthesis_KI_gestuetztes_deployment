terraform {
  backend "s3" {
    bucket = "terraform-state-bucket-415221799955-eu-central-1-an"
    key    = "state.tfstate"
    region = "eu-central-1"
  }
  required_version = ">= 1.5.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.0"
    }
  }    
}

provider "aws" {
  region = var.aws_region
}  

module "environments" {
  source   = "./modules/environments" // liest alle tf dateien in diesem ordner
  for_each = var.environments


  environment_name = each.key


  vpc_cidr               = each.value.vpc_cidr
  app_cpu                = each.value.app_cpu
  app_memory             = each.value.app_memory
  test_cpu               = each.value.test_cpu
  test_memory            = each.value.test_memory
  app_image_uri          = var.app_image_uri
  locust_image_uri       = var.locust_image_uri
  locust_test_user_count = each.value.locust_test_user_count
  locust_spawn_rate      = each.value.locust_spawn_rate
  locust_test_runtime    = each.value.locust_test_runtime
  s3_bucket_aws          = var.s3_bucket_aws
  variant_id             = var.variant_id
  target_method          = var.target_method
  postgres_host          = var.postgres_host
  postgres_port          = var.postgres_port
  postgres_user          = var.postgres_user
  postgres_password      = var.postgres_password
  postgres_db            = var.postgres_db
  jwt_secret_key         = var.jwt_secret_key
}
