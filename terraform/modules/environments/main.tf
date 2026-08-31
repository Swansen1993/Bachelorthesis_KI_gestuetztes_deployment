resource "aws_vpc" "enviroments_containers" {
  cidr_block           = var.vpc_cidr
  enable_dns_hostnames = true // ec2 instanzen können hostnamen bekommen
  enable_dns_support   = true // aktiviert interne dns auflösung (innerhalb vpc) auflösen zu können 
  tags                 = { Name = "vpc-${var.environment_name}" }
}  

resource "aws_subnet" "subnet_for_vpc" {
  vpc_id                  = aws_vpc.enviroments_containers.id // welche vpc vm soll weiter unterteilt werden ? 
  cidr_block              = cidrsubnet(var.vpc_cidr, 8, 1)    // Wird verwendet, um dynamisch den vorhandenen vpc bereich in kleinere subnets aufzuteilen, ist praktisch wenn wir mehrere Umgebungen dynamisch erzeugen. Bei einer einzelnen festen  Umgebung reicht auch cidr_block = "10.0.1.0/24"
  map_public_ip_on_launch = true                              // öffenliche ip adressen zuweisen um öffentliche endpunkte ansteurn zu könne (AWS ECR und AWS-S3 buckets) 
  tags                    = { Name = "subnet-${var.environment_name}" }
}

resource "aws_internet_gateway" "igw" {
  vpc_id = aws_vpc.enviroments_containers.id // Stellt einen internet zugang vom vpc aus zu.
}

resource "aws_route_table" "aws_rt_for_vpc" { // Route Table für den Internetzugang des Subnetzwerks
  vpc_id = aws_vpc.enviroments_containers.id
  route = [{
    cidr_block                 = "0.0.0.0/0"
    gateway_id                 = aws_internet_gateway.igw.id
    carrier_gateway_id         = null
    core_network_arn           = null
    destination_prefix_list_id = null
    egress_only_gateway_id     = null
    ipv6_cidr_block            = null
    local_gateway_id           = null
    nat_gateway_id             = null
    network_interface_id       = null
    transit_gateway_id         = null
    vpc_endpoint_id            = null
    vpc_peering_connection_id  = null
    odb_network_arn            = null
  }]
}

resource "aws_route_table_association" "rta" {
  subnet_id      = aws_subnet.subnet_for_vpc.id
  route_table_id = aws_route_table.aws_rt_for_vpc.id
}

resource "aws_ecs_cluster" "cluster_containers_in_vpc" {
  name = "cluster-${var.environment_name}"
}

resource "aws_service_discovery_private_dns_namespace" "discover_in_vpc" {
  name = "${var.environment_name}.lokalDNS"
  vpc  = aws_vpc.enviroments_containers.id
}

resource "aws_service_discovery_service" "app_discovery" {
  name = "app"
  dns_config {
    namespace_id = aws_service_discovery_private_dns_namespace.discover_in_vpc.id
    dns_records {
      ttl  = 10
      type = "A"
    }
  }
}

resource "aws_security_group" "app_security_rules" {
  name   = "app-sg-${var.environment_name}-app"
  vpc_id = aws_vpc.enviroments_containers.id // wir verwenden die separate Rule-Ressources da wir mehrere cidr blöcke haben ist es best practice die externen regeln anzuwenden 
}

resource "aws_vpc_security_group_ingress_rule" "ingressrulevpc" {
  security_group_id = aws_security_group.app_security_rules.id
  ip_protocol       = "tcp"
  from_port         = 8080
  to_port           = 8080
  cidr_ipv4         = cidrsubnet(var.vpc_cidr, 8, 1)
}

resource "aws_vpc_security_group_egress_rule" "egressrulevpc" {
  security_group_id = aws_security_group.app_security_rules.id
  ip_protocol       = "-1"
  cidr_ipv4         = "0.0.0.0/0"
}

resource "aws_iam_role" "aws_iam_execution_role" {
  name = "execution-role-${var.environment_name}"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action    = "sts:AssumeRole"
        Effect    = "Allow"
        Principal = { Service = "ecs-tasks.amazonaws.com" }
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "ecs_execute" {
  role       = aws_iam_role.aws_iam_execution_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

resource "aws_iam_role" "locust_runner_task_role" {
  name = "task-role-runner-${var.environment_name}"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action    = "sts:AssumeRole"
      Effect    = "Allow"
      Principal = { Service = "ecs-tasks.amazonaws.com" }
    }]
  })
}

resource "aws_iam_role_policy" "s3_write_policy" {
  name = "s3-write-${var.environment_name}"
  role = aws_iam_role.locust_runner_task_role.name
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action   = ["s3:PutObject"]
      Effect   = "Allow"
      Resource = "arn:aws:s3:::${var.s3_bucket_aws}/*"
    }]
  })
}

resource "aws_ecs_task_definition" "app_tasks" { // task definition legt die Parameter für die Container fest 
  family                   = "app-${var.environment_name}"
  execution_role_arn       = aws_iam_role.aws_iam_execution_role.arn
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  cpu                      = var.app_cpu
  memory                   = var.app_memory
  container_definitions = jsonencode([{
    name = "Application_container"
    environment = [
      { name = "TARGET_METHOD", value = var.target_method },
      { name = "S3_BUCKET", value = var.s3_bucket_aws }
    ]
    image     = var.app_image_uri
    essential = true
    portMappings = [{
      containerPort = 8080
    hostPort = 8080 }]
  }])
}

resource "aws_ecs_service" "app_service" { // aws_ecs_service ist die tatsächliche container Instanz
  name            = "run-app-tasks"
  desired_count   = 1
  cluster         = aws_ecs_cluster.cluster_containers_in_vpc.arn
  launch_type     = "FARGATE"
  task_definition = aws_ecs_task_definition.app_tasks.arn // Die eindeutige task definition verwenden die durch aws_ecs_task_definition.app_tasks erstellt wurde eine eindeutige zuordnung erfolgt durch die arn nummer (amazon ressource name)

  network_configuration {
    subnets          = [aws_subnet.subnet_for_vpc.id] // Array von subnets
    assign_public_ip = true
    security_groups  = [aws_security_group.app_security_rules.id] // Array von security_groups
  }
  service_registries {
    registry_arn = aws_service_discovery_service.app_discovery.arn
  }
}


resource "aws_ecs_task_definition" "runner_tasks" {
  family                   = "locust_test-${var.environment_name}"
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  cpu                      = var.test_cpu
  memory                   = var.test_memory
  execution_role_arn       = aws_iam_role.aws_iam_execution_role.arn
  task_role_arn            = aws_iam_role.locust_runner_task_role.arn


  container_definitions = jsonencode([{
    name      = "locust_test_runner"
    image     = var.locust_image_uri
    essential = true

    environment = [
      { name = "TARGET_METHOD", value = tostring(var.target_method) },
      { name = "TARGET_URL", value = "http://app.${var.environment_name}.local:8080" },
      { name = "LOCUST_USERS", value = tostring(var.locust_test_user_count) },
      { name = "LOCUST_SPAWN_RATE", value = tostring(var.locust_spawn_rate) },
      { name = "LOCUST_RUN_TIME", value = tostring(var.locust_test_runtime) },
      { name = "METRICS_S3_BUCKET", value = tostring(var.s3_bucket_aws) },
      { name = "S3_METRICS_PATH", value = "${var.variant_id}/${var.environment_name}/metrics.json" }
    ]
  }])
}
