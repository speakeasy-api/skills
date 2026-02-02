---
name: extract-openapi-spring
description: >-
  Use when extracting OpenAPI from Spring Boot using springdoc-openapi.
  Covers Maven/Gradle setup, annotations, polymorphism, and Speakeasy
  extensions. Triggers on "Spring Boot OpenAPI", "Spring SDK",
  "springdoc", "Spring API docs".
license: Apache-2.0
---

# extract-openapi-spring

Extract an OpenAPI specification from Spring Boot using springdoc-openapi.

## When to Use

- User has a Spring Boot application
- User wants to generate an SDK from Spring Boot
- User says: "Spring Boot OpenAPI", "springdoc", "Spring SDK"

## Installation

**Maven (pom.xml):**

```xml
<dependency>
    <groupId>org.springdoc</groupId>
    <artifactId>springdoc-openapi-starter-webmvc-ui</artifactId>
    <version>2.8.8</version>
</dependency>
```

**Gradle:**

```groovy
implementation 'org.springdoc:springdoc-openapi-starter-webmvc-ui:2.8.8'
```

## Configuration

**application.properties:**

```properties
springdoc.api-docs.path=/api-docs
springdoc.api-docs.version=OPENAPI_3_1
springdoc.swagger-ui.path=/swagger-ui.html
```

## Extraction

Spring Boot requires a running server:

```bash
./mvnw spring-boot:run &
sleep 15
curl http://localhost:8080/api-docs -o openapi.json
kill %1
```

## Application Metadata

```java
@SpringBootApplication
@OpenAPIDefinition(
    info = @Info(
        title = "Bookstore API",
        version = "1.0.0",
        description = "API for managing books"
    ),
    servers = {
        @Server(url = "https://api.example.com", description = "Production")
    }
)
public class Application { ... }
```

## Model Annotations

```java
@Schema(description = "Book publication")
public class Book {
    @Schema(description = "Unique ID", example = "123")
    private String id;

    @Schema(description = "Title", example = "Spring in Action")
    private String title;
}
```

## Adding Speakeasy Extensions

Create a custom `OperationCustomizer` bean:

```java
@Bean
public OperationCustomizer speakeasyCustomizer() {
    return (operation, handlerMethod) -> {
        // Add group based on controller name
        String group = handlerMethod.getBeanType()
            .getSimpleName()
            .replace("Controller", "")
            .toLowerCase();
        operation.addExtension("x-speakeasy-group", group);
        return operation;
    };
}
```

For global extensions, use `OpenApiCustomizer`:

```java
@Bean
public OpenApiCustomizer globalExtensions() {
    return openApi -> {
        openApi.addExtension("x-speakeasy-retries", Map.of(
            "strategy", "backoff",
            "statusCodes", List.of("5XX")
        ));
    };
}
```

## Post-Extraction

```bash
speakeasy lint openapi -s openapi.json
speakeasy quickstart -s openapi.json -t java -o ./sdk
```

## Related Skills

- `configure-speakeasy-extensions` - Add x-speakeasy-* extensions
- `manage-openapi-overlays` - Fix issues via overlay
