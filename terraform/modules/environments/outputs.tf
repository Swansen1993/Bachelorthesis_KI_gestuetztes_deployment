output "vpc_id" {
  value = aws_vpc.enviroments_containers.id
}

output "ecs_cluster_name" {
  value = aws_ecs_cluster.cluster_containers_in_vpc.name
}

output "app_service_name" {
  value = aws_ecs_service.app_service.name
}

output "dns_endpoint" {
  description = " lokaler DNS-Punkt "
  value       = "-app.${var.environment_name}.lokalDNS"
}
