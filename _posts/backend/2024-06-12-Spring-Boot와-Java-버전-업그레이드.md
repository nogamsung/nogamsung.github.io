---
layout: post
title: Spring Boot와 Java 버전 업그레이드
date: 2024-06-12
description: 
categories:
  - backend
  - spring
  - java
img: 
tags:
  - spring
  - java
toc: true
toc_sticky: true
toc_label: 목차
---
# 개요

회사에서 ISMS 심사를 받기로해 deprecated 된 버전들은 반드시 버전업을 해야 된다고 전해 받아 Spring Boot 2는 Spring 3으로 버전 업을 하게 됐다. 

물론 Spring Boot 2에서 사용되는 Java 11은 당장은 여유가 있지만 이번에 많은 프로젝트들을 버전업 시키면서 겸사겸사 하기로 결정됐다.

Java 11 ➡️ Java 21
Spring Boot 2.7.1 ➡️ Spring Boot 3.3.0

# 1️⃣ 자바 버전 업그레이드 및 스프링부트 2에서 최대 버전 업그레이드

먼저 스프링부트 버전을 2.7.x 버전, 즉 가장 최신 2 버전으로 맞춰서 라이브러리의 의존성을 확인한다.

#### 변경 전

###### `build.gradle`

```gradle
plugins {  
    id 'java'  
    id 'org.springframework.boot' version '2.7.1'  
    // ...
}

sourceCompatibility = '11'

dependencies {
	implementation 'mysql:mysql-connector-java'
	// ...
}
```

#### 변경 후

###### `build.gradle`

```gradle
plugins {  
    id 'java'  
    id 'org.springframework.boot' version '2.7.18'  
    // ...
}

sourceCompatibility = '21'

dependencies {
	implementation 'mysql:mysql-connector-java'
	// ...
}
```

# 2️⃣ 스프링부트 최신 버전 업그레이드

스프링부트 최신 버전으로 업그레이드한다. 아래와 같이 변경을 해주면 gradle build는 잘 돌아가게 된다.

#### 변경 전

###### `build.gradle`

```gradle
buildscript {  
    ext {  
       queryDslVersion = "5.0.0"
    }  
}

plugins {  
    id 'java'  
    id 'org.springframework.boot' version '2.7.18'  
    id 'io.spring.dependency-management' version '1.0.11.RELEASE'
    // ...
}

dependencies {
	implementation "com.querydsl:querydsl-jpa:${queryDslVersion}"  
	annotationProcessor "com.querydsl:querydsl-apt:5.0.0:jpa"  
	annotationProcessor("jakarta.persistence:jakarta.persistence-api")
	annotationProcessor("jakarta.annotation:jakarta.annotation-api")
	// ...
}
```

##### `gradle-wrapper.properties`

```properties
distributionUrl=https\://services.gradle.org/distributions/gradle-7.6.1-bin.zip
```

#### 변경 후

###### `build.gradle`

```gradle
plugins {  
    id 'java'  
    id 'org.springframework.boot' version '3.3.0'  
	id 'io.spring.dependency-management' version '1.1.5'
    // ...
}

dependencies {
	implementation 'com.querydsl:querydsl-core:5.0.0'  
	implementation 'com.querydsl:querydsl-jpa:5.0.0:jakarta'  
	annotationProcessor "com.querydsl:querydsl-apt:5.0.0:jakarta"  
	annotationProcessor 'jakarta.persistence:jakarta.persistence-api'  
	annotationProcessor 'jakarta.annotation:jakarta.annotation-api'
	// ...
}
```

##### `gradle-wrapper.properties`

```properties
distributionUrl=https\://services.gradle.org/distributions/gradle-8.7-bin.zip
```

# 3️⃣ 코드 변경

#### 변경 전

##### 전체

```java
import javax.persistence.*;
import javax.annotation.*;
import javax.validation.*;
import javax.servlet.*;
```

##### `SecurityConfig.java`

```java
@EnableWebSecurity  
@RequiredArgsConstructor
public class SecurityConfig {

	@Bean
	protected SecurityFilterChain configure(HttpSecurity http) throws Exception {
		http
			.csrf()
			.disable()  
			.exceptionHandling()  
			.authenticationEntryPoint(jwtAuthenticationEntryPoint)  
			.accessDeniedHandler(jwtAccessDeniedHandler)    
			.and()  
			.sessionManagement()  
			.sessionCreationPolicy(SessionCreationPolicy.STATELESS)  
			.and()  
			.authorizeRequests()  
			.antMatchers(WHITELIST).permitAll()  
			.anyRequest().authenticated()  
			.and()    
			.apply(new JwtSecurityConfig(tokenProvider));
			
		return http.build();
	}
}
```

#### 변경 후

##### 전체

```java
import jakarta.persistence.*;
import jakarta.annotation.*;
import jakarta.validation.*;
import jakarta.servlet.*;
```

##### `SecurityConfig.java`

```java
@Configuration  
@EnableWebSecurity  
@RequiredArgsConstructor
public class SecurityConfig {

	@Bean
	protected SecurityFilterChain configure(HttpSecurity http) throws Exception {
		http
			.csrf(AbstractHttpConfigurer::disable)  
			.exceptionHandling(customizer -> customizer.authenticationEntryPoint(jwtAuthenticationEntryPoint)  
                .accessDeniedHandler(jwtAccessDeniedHandler))  
	        .sessionManagement(customizer -> customizer.sessionCreationPolicy(SessionCreationPolicy.STATELESS))  
	        .authorizeHttpRequests(customizer ->  customizer.requestMatchers(AUTHENTICATE_LIST).authenticated()  
                .requestMatchers(PERMIT_LIST).permitAll()  
                .anyRequest().permitAll())  
		    .httpBasic(Customizer.withDefaults())  
	        .apply(new JwtSecurityConfig(tokenProvider));  
  
		return http.build();
	}
}
```

# 4️⃣ 마무리

- ECS와 같은 환경에서는 `buildspec.yml`도 바꿔야 된다
- `@Table(name = "schema.table)`로 Entity를 설정해 줬다면 더이상 읽지 못하기 때문에 `@Table(catalog = "schema", name = "table")`로 바꿔줘야 된다.
- Querydsl에 `Expressions.StringTemplate` 같은 코드도 수정이 필요하기 때문에 모든 API들에 코드들을 점검해야 한다.

# 참조

- https://luvstudy.tistory.com/221
- https://hodolman.com/54
- https://github.com/spring-projects/spring-boot/wiki/Spring-Boot-3.0-Migration-Guide