output "environment_summary" {
  description = "Zusammenfasssung der Umgebungen"
  value = {
    for env, mod in module.environments : env => {
      vpc_id           = mod.vpc_id
      ecs_cluster_name = mod.ecs_cluster_name
      app_service_name = mod.app_service_name
      dns_endpoint     = mod.dns_endpoint
    }
  }
}

output "environment_infos" {
  value = {
    for env, mod in module.environments : env => {
      cluster_name       = mod.ecs_cluster_name
      runner_task_family = mod.runner_task_family
      app_task_family    = mod.app_task_family
      security_group_id  = mod.app_security_group_id
      subnet_id          = mod.subnet_id
      db_address         = mod.db_address
      db_port            = mod.db_port
      db_name            = var.db_name
      db_username        = var.db_username
      target_url         = "http://app.${env}.local:8080"
    }
  }
}
