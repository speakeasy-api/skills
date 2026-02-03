# Spring Boot OpenAPI Extraction

Detailed guide for extracting OpenAPI specs from Spring Boot using springdoc-openapi.

## Installation

### Maven

```xml
<dependency>
    <groupId>org.springdoc</groupId>
    <artifactId>springdoc-openapi-starter-webmvc-ui</artifactId>
    <version>2.3.0</version>
</dependency>
```

### Gradle

```groovy
implementation 'org.springdoc:springdoc-openapi-starter-webmvc-ui:2.3.0'
```

## Configuration

```yaml
# application.yml
springdoc:
  api-docs:
    path: /v3/api-docs
  swagger-ui:
    path: /swagger-ui.html
  info:
    title: My API
    version: 1.0.0
    description: API description with **markdown** support
  servers:
    - url: https://api.example.com
      description: Production
    - url: https://staging.example.com
      description: Staging
```

Or via Java configuration:

```java
@Configuration
public class OpenApiConfig {
    @Bean
    public OpenAPI customOpenAPI() {
        return new OpenAPI()
            .info(new Info()
                .title("My API")
                .version("1.0.0")
                .description("API description"))
            .addServersItem(new Server()
                .url("https://api.example.com")
                .description("Production"));
    }
}
```

## Extraction

```bash
# Start application
./mvnw spring-boot:run &
sleep 15

# Fetch spec
curl http://localhost:8080/v3/api-docs -o openapi.json

# Or YAML
curl http://localhost:8080/v3/api-docs.yaml -o openapi.yaml
```

## Controller Documentation

### Basic Controller

```java
import io.swagger.v3.oas.annotations.*;
import io.swagger.v3.oas.annotations.responses.*;
import io.swagger.v3.oas.annotations.tags.*;

@RestController
@RequestMapping("/burgers")
@Tag(name = "burgers", description = "Burger operations")
public class BurgerController {

    @GetMapping
    @Operation(
        summary = "List burgers",
        description = "Returns a paginated list of all burgers",
        operationId = "listBurgers"
    )
    @ApiResponses({
        @ApiResponse(responseCode = "200", description = "Success",
            content = @Content(array = @ArraySchema(schema = @Schema(implementation = Burger.class)))),
        @ApiResponse(responseCode = "400", description = "Invalid parameters")
    })
    public List<Burger> findAll(
        @Parameter(description = "Page size") @RequestParam(defaultValue = "20") int limit,
        @Parameter(description = "Page offset") @RequestParam(defaultValue = "0") int offset
    ) {
        // ...
    }

    @GetMapping("/{id}")
    @Operation(summary = "Get burger", operationId = "getBurger")
    @ApiResponses({
        @ApiResponse(responseCode = "200", description = "Burger found"),
        @ApiResponse(responseCode = "404", description = "Burger not found")
    })
    public Burger findById(@PathVariable String id) {
        // ...
    }

    @PostMapping
    @Operation(summary = "Create burger", operationId = "createBurger")
    @ApiResponse(responseCode = "201", description = "Burger created")
    public ResponseEntity<Burger> create(@RequestBody @Valid CreateBurgerRequest request) {
        // ...
    }
}
```

## DTOs with Schema

```java
import io.swagger.v3.oas.annotations.media.Schema;

@Schema(description = "Burger representation")
public class Burger {
    @Schema(description = "Unique identifier", example = "123")
    private String id;

    @Schema(description = "Burger name", example = "Classic Burger", maxLength = 100)
    private String name;

    @Schema(description = "Price in USD", example = "9.99", minimum = "0.01")
    private BigDecimal price;

    @Schema(description = "Optional description")
    private String description;

    // getters/setters
}

@Schema(description = "Create burger request")
public class CreateBurgerRequest {
    @Schema(description = "Burger name", required = true, example = "Classic Burger")
    @NotBlank
    @Size(max = 100)
    private String name;

    @Schema(description = "Price in USD", required = true, example = "9.99")
    @NotNull
    @Positive
    private BigDecimal price;

    @Schema(description = "Optional description")
    private String description;

    // getters/setters
}
```

## Speakeasy Extensions

### Via OperationCustomizer

```java
@Configuration
public class OpenApiConfig {
    @Bean
    public OperationCustomizer operationCustomizer() {
        return (operation, handlerMethod) -> {
            // Add group based on controller name
            String controllerName = handlerMethod.getBeanType()
                .getSimpleName()
                .replace("Controller", "")
                .toLowerCase();
            operation.addExtension("x-speakeasy-group", controllerName);
            return operation;
        };
    }
}
```

### Per-Operation Extensions

```java
@GetMapping
@Operation(
    summary = "List burgers",
    operationId = "listBurgers",
    extensions = {
        @Extension(name = "x-speakeasy-group", properties = @ExtensionProperty(name = "", value = "burgers")),
        @Extension(name = "x-speakeasy-name-override", properties = @ExtensionProperty(name = "", value = "list"))
    }
)
public List<Burger> findAll() {
    // ...
}
```

### Global Retries

```java
@Bean
public OpenApiCustomizer openApiCustomizer() {
    return openApi -> {
        Map<String, Object> retries = new HashMap<>();
        retries.put("strategy", "backoff");
        Map<String, Object> backoff = new HashMap<>();
        backoff.put("initialInterval", 500);
        backoff.put("maxInterval", 60000);
        backoff.put("exponent", 1.5);
        retries.put("backoff", backoff);
        retries.put("statusCodes", List.of("5XX", "429"));

        openApi.addExtension("x-speakeasy-retries", retries);
    };
}
```

## Authentication

### Security Schemes

```java
@Configuration
public class OpenApiConfig {
    @Bean
    public OpenAPI customOpenAPI() {
        return new OpenAPI()
            .components(new Components()
                .addSecuritySchemes("bearer-auth",
                    new SecurityScheme()
                        .type(SecurityScheme.Type.HTTP)
                        .scheme("bearer")
                        .bearerFormat("JWT"))
                .addSecuritySchemes("api-key",
                    new SecurityScheme()
                        .type(SecurityScheme.Type.APIKEY)
                        .in(SecurityScheme.In.HEADER)
                        .name("X-API-Key")))
            .addSecurityItem(new SecurityRequirement().addList("bearer-auth"));
    }
}
```

### Per-Operation Security

```java
@GetMapping("/admin")
@Operation(
    summary = "Admin endpoint",
    security = @SecurityRequirement(name = "bearer-auth")
)
public void adminEndpoint() {
    // ...
}

@GetMapping("/public")
@Operation(
    summary = "Public endpoint",
    security = {}  // No auth required
)
public void publicEndpoint() {
    // ...
}
```

## Pagination

```java
@GetMapping
@Operation(
    summary = "List burgers",
    extensions = {
        @Extension(name = "x-speakeasy-pagination", properties = {
            @ExtensionProperty(name = "type", value = "offsetLimit"),
            // Complex nested objects need JSON string
        })
    }
)
@PageableAsQueryParam
public Page<Burger> findAll(@ParameterObject Pageable pageable) {
    // ...
}
```

## File Upload

```java
@PostMapping(value = "/upload", consumes = MediaType.MULTIPART_FORM_DATA_VALUE)
@Operation(summary = "Upload image")
public ResponseEntity<String> uploadImage(
    @Parameter(description = "Image file", content = @Content(mediaType = MediaType.MULTIPART_FORM_DATA_VALUE))
    @RequestParam("file") MultipartFile file
) {
    // ...
}
```

## Groups and Tags

```java
// Group by package
springdoc.group-configs[0].group=burgers
springdoc.group-configs[0].paths-to-match=/burgers/**
springdoc.group-configs[1].group=orders
springdoc.group-configs[1].paths-to-match=/orders/**

// Or via annotation
@Tag(name = "burgers", description = "Burger operations",
    externalDocs = @ExternalDocumentation(
        description = "Learn more",
        url = "https://example.com/docs/burgers"
    ))
```

## Common Issues

| Issue | Solution |
|-------|----------|
| Endpoints not showing | Check `@RestController` and component scan |
| Missing schemas | Add `@Schema` annotations to DTOs |
| Wrong content type | Use `produces`/`consumes` in mapping |
| Security not applied | Add `@SecurityRequirement` or global security |
