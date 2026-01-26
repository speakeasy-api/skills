---
short_description: Extract OpenAPI from Spring Boot using springdoc-openapi
long_description: Spring Boot applications use springdoc-openapi for OpenAPI generation. This guide covers annotations for models, endpoints, polymorphism, and customization for better SDK generation.
source:
  repo: "speakeasy-api/speakeasy.com"
  path: "src/content/openapi/frameworks/springboot.mdx"
  ref: "af7c36a9ec957336fb799151a4e5af3ae293831e"
  last_reconciled: "2025-12-11"
---

# Spring Boot OpenAPI Extraction

Spring Boot uses `springdoc-openapi` library for OpenAPI generation.

## Installation

**Maven (pom.xml)**:

```xml
<dependency>
    <groupId>org.springdoc</groupId>
    <artifactId>springdoc-openapi-starter-webmvc-ui</artifactId>
    <version>2.8.8</version>
</dependency>
```

## Configuration

**application.properties**:

```properties
springdoc.api-docs.path=/api-docs
springdoc.api-docs.version=OPENAPI_3_1
springdoc.swagger-ui.path=/swagger-ui.html
```

Access points:
- OpenAPI document: `http://localhost:8080/api-docs`
- Swagger UI: `http://localhost:8080/swagger-ui.html`

## Application Definition

```java
import io.swagger.v3.oas.annotations.OpenAPIDefinition;
import io.swagger.v3.oas.annotations.info.Contact;
import io.swagger.v3.oas.annotations.info.Info;
import io.swagger.v3.oas.annotations.info.License;
import io.swagger.v3.oas.annotations.servers.Server;

@SpringBootApplication
@OpenAPIDefinition(
    info = @Info(
        title = "Bookstore API",
        version = "1.0.0",
        description = "This API provides endpoints to manage a bookstore's inventory",
        contact = @Contact(
            name = "Bookstore API Support",
            email = "api@bookstore.example.com",
            url = "https://bookstore.example.com/support"
        ),
        license = @License(
            name = "Apache 2.0",
            url = "https://www.apache.org/licenses/LICENSE-2.0.html"
        )
    ),
    servers = {
        @Server(url = "https://api.bookstore.example.com", description = "Production server"),
        @Server(url = "http://localhost:8080", description = "Development server")
    }
)
public class BookstoreApplication {
    public static void main(String[] args) {
        SpringApplication.run(BookstoreApplication.class, args);
    }
}
```

## Model Annotations

```java
import io.swagger.v3.oas.annotations.media.Schema;

@Schema(description = "Book publication with author and ISBN")
class Book {
    @Schema(description = "Unique identifier", example = "123e4567-e89b-12d3-a456-426614174000")
    private String id;

    @Schema(description = "Title of the publication", example = "Spring Boot in Action")
    private String title;

    @Schema(description = "Author of the book", example = "Craig Walls")
    private String author;

    @Schema(description = "ISBN of the book", example = "978-1617292545")
    private String isbn;
}
```

## Polymorphic Models

```java
import com.fasterxml.jackson.annotation.JsonTypeInfo;
import com.fasterxml.jackson.annotation.JsonSubTypes;

@Schema(description = "Base class for all publications")
@JsonTypeInfo(
    use = JsonTypeInfo.Id.NAME,
    property = "type",
    visible = true
)
@JsonSubTypes({
    @JsonSubTypes.Type(value = Book.class, name = "BOOK"),
    @JsonSubTypes.Type(value = Magazine.class, name = "MAGAZINE")
})
public abstract class Publication {
    @Schema(description = "Type of publication", example = "BOOK", allowableValues = {"BOOK", "MAGAZINE"})
    protected abstract String getType();
}
```

## Controller Documentation

```java
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import io.swagger.v3.oas.annotations.media.Content;
import io.swagger.v3.oas.annotations.media.Schema;
import io.swagger.v3.oas.annotations.responses.ApiResponse;
import io.swagger.v3.oas.annotations.responses.ApiResponses;
import io.swagger.v3.oas.annotations.tags.Tag;

@RestController
@RequestMapping("/publications")
@Tag(name = "Publications", description = "Operations for managing publications")
public class PublicationsController {

    @Operation(
        summary = "Get a publication by ID",
        description = "Returns a single publication (book or magazine)"
    )
    @ApiResponses(value = {
        @ApiResponse(
            responseCode = "200",
            description = "Successful operation",
            content = @Content(schema = @Schema(oneOf = {Book.class, Magazine.class}))
        ),
        @ApiResponse(
            responseCode = "404",
            description = "Publication not found",
            content = @Content(schema = @Schema(implementation = ErrorResponse.class))
        )
    })
    @GetMapping("/{id}")
    public ResponseEntity<?> getPublication(
        @Parameter(description = "ID of the publication to return", required = true)
        @PathVariable String id
    ) {
        // Implementation
    }
}
```

## Speakeasy Extensions

```java
import io.swagger.v3.oas.annotations.extensions.Extension;
import io.swagger.v3.oas.annotations.extensions.ExtensionProperty;

@Operation(
    summary = "List all publications",
    description = "Get a list of all publications in the store",
    extensions = {
        @Extension(name = "x-speakeasy-retries", properties = {
            @ExtensionProperty(name = "strategy", value = "backoff"),
            @ExtensionProperty(name = "backoff", parseValue = true,
                value = "{\"initialInterval\":500,\"maxInterval\":60000,\"maxElapsedTime\":3600000,\"exponent\":1.5}"),
            @ExtensionProperty(name = "statusCodes", parseValue = true, value = "[\"5XX\"]"),
            @ExtensionProperty(name = "retryConnectionErrors", parseValue = true, value = "true")
        })
    }
)
@GetMapping
public ResponseEntity<List<Publication>> listPublications() {
    // Implementation
}
```

## OpenAPI Generation

```bash
./mvnw clean install
./mvnw spring-boot:run
curl http://localhost:8080/api-docs.yaml -o openapi.yaml
```

## Validation

```bash
speakeasy validate openapi -s openapi.yaml
```

## SDK Generation

```bash
speakeasy quickstart --schema openapi.yaml --target typescript --out-dir ./sdk
```

## Reference

- springdoc-openapi: https://springdoc.org
- Spring Boot: https://spring.io/projects/spring-boot
- Swagger annotations: https://github.com/swagger-api/swagger-core/wiki/Swagger-2.X---Annotations

---

## Pre-defined TODO List

When extracting OpenAPI from Spring Boot, initialize your TODO list with:

| Step | TODO Item | Active Form |
|------|-----------|-------------|
| 1 | Verify Spring Boot application exists | Verifying Spring Boot application exists |
| 2 | Add springdoc-openapi dependency to pom.xml or build.gradle | Adding springdoc-openapi dependency |
| 3 | Configure OpenAPI metadata in application.properties | Configuring OpenAPI metadata |
| 4 | Add @Operation and @Schema annotations to controllers | Adding annotations to controllers |
| 5 | Start Spring Boot application | Starting Spring Boot application |
| 6 | Access OpenAPI spec at /v3/api-docs endpoint | Accessing OpenAPI spec endpoint |
| 7 | Validate spec with speakeasy validate | Validating spec with speakeasy validate |

**Usage:**
```
TodoWrite([
  {content: "Verify Spring Boot application exists", status: "pending", activeForm: "Verifying Spring Boot application exists"},
  {content: "Add springdoc-openapi dependency to pom.xml or build.gradle", status: "pending", activeForm: "Adding springdoc-openapi dependency"},
  {content: "Configure OpenAPI metadata in application.properties", status: "pending", activeForm: "Configuring OpenAPI metadata"},
  {content: "Add @Operation and @Schema annotations to controllers", status: "pending", activeForm: "Adding annotations to controllers"},
  {content: "Start Spring Boot application", status: "pending", activeForm: "Starting Spring Boot application"},
  {content: "Access OpenAPI spec at /v3/api-docs endpoint", status: "pending", activeForm: "Accessing OpenAPI spec endpoint"},
  {content: "Validate spec with speakeasy validate", status: "pending", activeForm: "Validating spec with speakeasy validate"}
])
```

**Nested workflows:**
- For validation issues, see `spec-first/validation.md`
- For SDK generation after extraction, see `plans/sdk-generation.md`

