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
  description = " lokaler DNS Punkt "
  value       = "-app.${var.environment_name}.local"
}

output "runner_task_family" {
  value = aws_ecs_task_definition.runner_tasks.family
}

output "app_task_family" {
  value = aws_ecs_task_definition.app_tasks.family
}

output "app_security_group_id" {
  value = aws_security_group.app_security_rules.id
}

output "subnet_id" {
  value = aws_subnet.subnet_for_vpc.id
}

output "db_address" {
  value = aws_db_instance.app_db.address
}

output "db_port" {
  value = 5432
}

