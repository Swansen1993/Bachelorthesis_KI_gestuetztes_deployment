environments = {
  "low" = {
    vpc_cidr               = "10.1.0.0/16"
    app_memory             = "1024"
    app_cpu                = "512"
    test_memory            = "1024"
    test_cpu               = "512"
    locust_test_user_count = 50
    locust_spawn_rate      = 3
    locust_test_runtime    = "30s"
  }
  "medium" = {
    vpc_cidr               = "10.2.0.0/16"
    app_memory             = "1024"
    app_cpu                = "512"
    test_memory            = "1024"
    test_cpu               = "512"
    locust_test_user_count = 200
    locust_spawn_rate      = 7
    locust_test_runtime    = "60s"
  }
  "high" = {
    vpc_cidr               = "10.3.0.0/16"
    app_memory             = "1024"
    app_cpu                = "512"
    test_memory            = "2048"
    test_cpu               = "1024"
    locust_test_user_count = 1000
    locust_spawn_rate      = 22
    locust_test_runtime    = "90s"
  }
  "extreme" = {
    vpc_cidr               = "10.4.0.0/16"
    app_memory             = "1024"
    app_cpu                = "512"
    test_memory            = "4096"
    test_cpu               = "2048"
    locust_test_user_count = 3000
    locust_spawn_rate      = 50
    locust_test_runtime    = "120s"
  }
  "prod" = {
    vpc_cidr               = "10.5.0.0/16"
    app_cpu                = "512"
    app_memory             = "1024"
    test_cpu               = "512"
    test_memory            = "1024"
    locust_test_user_count = 100
    locust_spawn_rate      = 5
    locust_test_runtime    = "60s"
  }
}
