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
