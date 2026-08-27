import os
import uuid
from locust import HttpUser, task , between

ACTIVE_TARGET = os.getenv("TARGET_METHOD", "pos_001")

class Projekt01Tests(HttpUser):
    wait_time = between(0.1, 0.3)
    
    def on_start(self):
        "Vor Testbeginn einen Nutzer erstellen"
        self.username = f"user_{uuid.uuid4().hex[8]}"
        self.email = f"user_{self.username}@test.com"
        self.password = "benchmarkPW123!"
        self.token =""
        self.headers = {}
        self.target_slug = "bench-article-initialising"
        
        "user regisitrieren"
        reg_res = self.client.post(
            "/api/users",
            json= {"user" : {"username" : self.username, 
                             "email" : self.email,
                             "password" : self.password}}
        )
        
        if reg_res.status_code in [200,201]:
            data = reg_res.json()
            self.token = data.get("user" , {}).get("token", "")
            self.headers = {"Authorization" : f"token {self.token}"}
            
            
        if self.token:
            art_res = self.client.post(
                "/api/articles",
                json={"article": {"title": f"Init Article {self.username}", "description": "Init", "body": "Body"}},
                headers=self.headers
            )
            if art_res.status_code in [200, 201]:
                self.target_slug = art_res.json().get("article", {}).get("slug", self.target_slug)
                
                
    
@task(1 if ACTIVE_TARGET == "pos_001_post_add_article" else 0) 
def add_article_test (self):
    unique_id = uuid.uuid4().hex[8]
    
    payload= {"article":{
        "title" :f" test_title{unique_id}",
        "description" : "Beschreibung artikel test",
        "body":"Testartikel inhalt",
    }}
    
    self.client.post("api/articles",
                     json = payload,
                     headers = self.headers,
                     name = "/api/articles [POST add]")



@task(1 if ACTIVE_TARGET == "pos_002_get_list_by_filters" else 0) 
def list_by_filters_get(self):
    self.client.get(
        "/api/articles?limit=10&offset=0",
        headers=self.headers,
        name="/api/articles [GET list_by_filters]"
    )
    
    
    
@task(1 if ACTIVE_TARGET == "pos_003_post_article_add_many_tag" else 0) 
def add_many(self):
  unique_suffix = uuid.uuid4().hex[8]
  
  payload2= {"article":{
      "title": f" test_title{unique_suffix}",
      "description":"Tagliste Artikel",
      "body":"Beschreibung der tagliste",
      "tagList": [f" tag_a{unique_suffix}", f"tag_b{unique_suffix}", "performance"]
  }}
  
  self.client.post(
      "api/articles",
      json=payload2,
      headers=self.headers,
      name="api/articles [POST add_many]"
      )
  
@task(1 if ACTIVE_TARGET == "pos_004_get_articles_favorite_exists" else 0)
def bench_favorite_exists(self):
        self.client.get(
            f"/api/articles/{self.target_slug}",
            headers=self.headers,
            name="/api/articles/:slug [favorite_exists]"
        )

@task(1 if ACTIVE_TARGET == "pos_005_post_article_comment_into_repository" else 0)
def bench_comment_add(self):
    self.client.post(
        f"/api/articles/{self.target_slug}/comments",
        json={"comment" : {"body": f"benchmark comment {uuid.uuid4().hex[8]}"}},
        headers= self.headers,
        name= "/api/articles/: slug/comments [comment_add]"
    )

@task(1 if ACTIVE_TARGET == "pos_006_get_follower_list" else 0)
def bench_follower_list(self):
        self.client.get(
            f"/api/profiles/{self.username}",
            headers=self.headers,
            name="/api/profiles/:username [follower_list]"
        )


@task(1 if ACTIVE_TARGET == ["pos_007_post_create_follow_in_repository", "pos_012_post_follow_user"] else 0)
def bench_create_follow(self):
    self.client.post(
        f"/api/profiles/{self.username}/follow",
        headers=self.headers,
        name= "/api/profiles/:username/follow [follow_user]"
    )


@task(1 if ACTIVE_TARGET == "sign_in_user" else 0)
def bench_sign_in_user(self):
        self.client.post(
            "/api/users/login",
            json={"user": {"email": self.email, "password": self.password}},
            name="/api/users/login [sign_in_user]"
        )
        
        