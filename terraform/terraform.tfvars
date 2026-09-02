environments = {
  "low" = {
    vpc_cidr               = "10.1.0.0/16"
    app_memory             = "2048"
    app_cpu                = "1024"
    test_memory            = "1024"
    test_cpu               = "512"
    locust_test_user_count = 10
    locust_spawn_rate      = 1
    locust_test_runtime    = "30s"
  }

  "medium" = {
    vpc_cidr               = "10.2.0.0/16"
    app_memory             = "2048"
    app_cpu                = "1024"
    test_memory            = "1024"
    test_cpu               = "512"
    locust_test_user_count = 25
    locust_spawn_rate      = 2
    locust_test_runtime    = "60s"
  }
  "high" = {
    vpc_cidr               = "10.3.0.0/16"
    app_memory             = "2048"
    app_cpu                = "1024"
    test_memory            = "2048"
    test_cpu               = "1024"
    locust_test_user_count = 40
    locust_spawn_rate      = 3
    locust_test_runtime    = "90s"
  }
  "extreme" = {
    vpc_cidr               = "10.4.0.0/16"
    app_memory             = "2048"
    app_cpu                = "1024"
    test_memory            = "4096"
    test_cpu               = "2048"
    locust_test_user_count = 50
    locust_spawn_rate      = 4
    locust_test_runtime    = "120s"
  }
 "prod" = {
    vpc_cidr               = "10.5.0.0/16"
    app_memory             = "2048"
    app_cpu                = "1024"
    test_cpu               = "512"
    test_memory            = "1024"
    locust_test_user_count = 25
    locust_spawn_rate      = 2
    locust_test_runtime    = "60s"
  }
}