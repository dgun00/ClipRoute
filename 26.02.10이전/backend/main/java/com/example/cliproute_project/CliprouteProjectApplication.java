package com.example.cliproute_project;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.data.jpa.repository.config.EnableJpaAuditing;

@SpringBootApplication
@EnableJpaAuditing
public class CliprouteProjectApplication {

    public static void main(String[] args) {
        SpringApplication.run(CliprouteProjectApplication.class, args);
    }

}
