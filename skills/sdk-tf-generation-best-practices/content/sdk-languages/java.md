---
short_description: "Java SDK generation guide"
long_description: |
  Comprehensive guide for generating Java SDKs with Speakeasy.
  Includes methodology, feature support, Gradle/Maven configuration,
  Maven Central publishing, and build customization patterns.
source:
  repo: "codatio/client-sdk-java"
  path: "lending/.speakeasy/gen.yaml, lending/build.gradle"
  ref: "main"
  last_reconciled: "2025-12-11"
---

# Java SDK Generation

## SDK Overview

Speakeasy-generated Java SDKs are idiomatic Java libraries designed for modern Java development (Java 11+). They use Jackson for JSON serialization, Apache HttpClient for HTTP requests, and follow builder patterns for configuration.

Core features:

- Strongly typed models with Jackson annotations
- Builder pattern for all request and response types
- Fluent API design for SDK methods
- Built-in retry support with configurable backoff
- Optional pagination support for supported APIs
- Authentication support for OAuth flows and standard security mechanisms
- Complex number types including BigInteger and BigDecimal
- Date and date/time types using Java 8 time API
- Custom type enums using strings and integers

### Java Package Structure

```
{artifactId}/
├── .speakeasy/
│   ├── gen.yaml              # Generation configuration
│   └── gen.lock              # Version lock
├── src/main/java/{package}/
│   ├── {SDKClassName}.java   # Main SDK entry point
│   ├── *.java                # Operation classes (per tag)
│   ├── models/
│   │   ├── shared/           # Shared component types
│   │   ├── operations/       # Request/response types
│   │   └── errors/           # Error types
│   └── utils/                # Internal utilities
├── docs/
│   ├── models/               # Model documentation
│   └── sdks/                 # Operation documentation
├── build.gradle              # Generated Gradle build
├── build-extras.gradle       # Customization (not overwritten)
├── settings.gradle           # Project settings
├── README.md                 # SDK documentation
├── USAGE.md                  # Quick start examples
└── RELEASES.md               # Release history
```

## Client Construction

Speakeasy Java SDKs use the builder pattern for client instantiation:

```java
import io.example.MySdk;
import io.example.models.shared.Security;

// Basic construction with API key
MySdk sdk = MySdk.builder()
    .security(Security.builder()
        .authHeader("Basic BASE_64_ENCODED(API_KEY)")
        .build())
    .build();

// With custom server URL
MySdk sdk = MySdk.builder()
    .serverURL("https://api.example.com")
    .security(Security.builder()
        .authHeader("Bearer TOKEN")
        .build())
    .build();
```

### Making API Calls

Operations follow a fluent pattern:

```java
import io.example.models.operations.*;
import io.example.models.shared.*;

// Create a resource
CreateResourceResponse response = sdk.resources().create()
    .request(CreateResourceRequest.builder()
        .name("my-resource")
        .description("A sample resource")
        .build())
    .call();

if (response.resource().isPresent()) {
    Resource resource = response.resource().get();
    System.out.println("Created: " + resource.id());
}

// List resources with pagination
ListResourcesResponse listResponse = sdk.resources().list()
    .request(ListResourcesRequest.builder()
        .page(1)
        .pageSize(50)
        .build())
    .call();
```

## Type Safety

### Generated Models

Speakeasy uses Jackson annotations for all generated models to correctly serialize and deserialize objects:

```java
public class Resource {
    @JsonProperty("id")
    private String id;

    @JsonProperty("name")
    private String name;

    @JsonProperty("created_at")
    private OffsetDateTime createdAt;

    @JsonProperty("status")
    private ResourceStatus status;

    // Builder pattern for construction
    public static Builder builder() {
        return new Builder();
    }

    public static class Builder {
        private String id;
        private String name;
        private OffsetDateTime createdAt;
        private ResourceStatus status;

        public Builder id(String id) {
            this.id = id;
            return this;
        }
        // ... other setters

        public Resource build() {
            return new Resource(id, name, createdAt, status);
        }
    }
}
```

### Optional Fields

Optional fields use `java.util.Optional`:

```java
// Check if optional field is present
if (response.resource().isPresent()) {
    Resource resource = response.resource().get();
    // Use the resource
}

// Or use orElse for defaults
Resource resource = response.resource().orElse(defaultResource);
```

### Enum Types

Enums are generated as Java enums:

```java
public enum ResourceStatus {
    @JsonProperty("active")
    ACTIVE("active"),

    @JsonProperty("pending")
    PENDING("pending"),

    @JsonProperty("deleted")
    DELETED("deleted");

    private final String value;

    ResourceStatus(String value) {
        this.value = value;
    }

    public String value() {
        return value;
    }
}
```

## Error Handling

The Java SDK uses typed exceptions for error handling:

```java
import io.example.models.errors.SDKError;
import io.example.models.errors.ErrorMessage;

try {
    CreateResourceResponse response = sdk.resources().create()
        .request(request)
        .call();

    if (response.resource().isPresent()) {
        // Handle success
    }
} catch (ErrorMessage e) {
    // Handle API-specific error (4xx/5xx with error body)
    System.err.println("API Error: " + e.getMessage());
    System.err.println("Status Code: " + e.statusCode());
} catch (SDKError e) {
    // Handle generic SDK errors
    System.err.println("SDK Error: " + e.getMessage());
} catch (Exception e) {
    // Handle unexpected errors
    System.err.println("Unexpected error: " + e.getMessage());
}
```

### Error Response Types

When the OpenAPI spec defines error responses, the SDK generates typed error classes:

```java
// Specific error types from spec
catch (BadRequestError e) {
    // 400 errors
    System.err.println("Validation failed: " + e.errors());
} catch (UnauthorizedError e) {
    // 401 errors
    System.err.println("Authentication failed");
} catch (NotFoundError e) {
    // 404 errors
    System.err.println("Resource not found: " + e.resourceId());
}
```

## Configuration Options

All Java SDK configuration is managed in the `gen.yaml` file under the `java` section.

### Version and General Configuration

```yaml
java:
  version: 1.0.0
  artifactID: my-sdk
  groupID: io.example
  author: Example Inc
  companyName: Example Inc
  companyEmail: support@example.com
  companyURL: https://www.example.com/
```

| Name | Required | Default | Description |
|------|----------|---------|-------------|
| version | true | 0.0.1 | SDK version published to Maven |
| artifactID | true | openapi | Maven artifact ID |
| groupID | true | io.example | Maven group ID |
| author | false | Speakeasy | Author in POM metadata |
| companyName | false | null | Company name in POM |
| companyEmail | false | null | Support email in POM |
| companyURL | false | null | Company URL in POM |

### SDK Class Configuration

```yaml
generation:
  sdkClassName: MySdk
java:
  projectName: openapi
  description: "Java SDK for My API"
```

| Name | Required | Default | Description |
|------|----------|---------|-------------|
| sdkClassName | false | SDK | Name of the main SDK class |
| projectName | false | openapi | Internal project name |
| description | false | null | SDK description for POM |

### Method and Parameter Configuration

```yaml
java:
  maxMethodParams: 0
  inputModelSuffix: input
  outputModelSuffix: output
```

| Name | Required | Default | Description |
|------|----------|---------|-------------|
| maxMethodParams | false | 0 | Max parameters before request object is used. 0 means always use request objects. |
| inputModelSuffix | false | input | Suffix for input model classes |
| outputModelSuffix | false | output | Suffix for output model classes |

### Security Configuration

```yaml
java:
  flattenGlobalSecurity: false
```

| Name | Required | Default | Description |
|------|----------|---------|-------------|
| flattenGlobalSecurity | false | true | Enables inline security credentials during SDK instantiation |

### Error Handling Configuration

```yaml
java:
  clientServerStatusCodesAsErrors: true
  defaultErrorName: SDKError
```

| Name | Required | Default | Description |
|------|----------|---------|-------------|
| clientServerStatusCodesAsErrors | false | true | Treat 4XX and 5XX status codes as errors |
| defaultErrorName | false | SDKError | Name for generic error class |

### Import Path Configuration

```yaml
java:
  imports:
    option: openapi
    paths:
      callbacks: models/callbacks
      errors: models/errors
      operations: models/operations
      shared: models/shared
      webhooks: models/webhooks
```

| Path | Default | Description |
|------|---------|-------------|
| callbacks | models/callbacks | Callback model package |
| errors | models/errors | Error model package |
| operations | models/operations | Operation request/response package |
| shared | models/shared | Shared component package |
| webhooks | models/webhooks | Webhook model package |

### License Configuration

```yaml
java:
  license:
    name: The MIT License (MIT)
    shortName: MIT
    url: https://mit-license.org/
```

### GitHub Configuration

```yaml
java:
  githubURL: github.com/example/my-sdk
```

## Build Customization with build-extras.gradle

The generated `build.gradle` includes a hook for customizations that won't be overwritten during regeneration:

```groovy
// At the end of generated build.gradle
apply from: 'build-extras.gradle'
```

### Creating build-extras.gradle

Create `build-extras.gradle` in your SDK root for customizations:

```groovy
// build-extras.gradle
// This file is NOT overwritten during SDK regeneration

// Add extra dependencies
dependencies {
    implementation 'org.slf4j:slf4j-api:2.0.9'
    testImplementation 'org.junit.jupiter:junit-jupiter:5.10.0'
}

// Configure additional compiler options
compileJava {
    options.compilerArgs += ['-parameters']
}

// Add custom tasks
task myCustomTask {
    doLast {
        println 'Running custom task'
    }
}
```

### Common Customizations

**Adding Test Dependencies:**

```groovy
dependencies {
    testImplementation 'org.mockito:mockito-core:5.8.0'
    testImplementation 'org.assertj:assertj-core:3.24.2'
}

test {
    useJUnitPlatform()
}
```

**Configuring Java Version:**

```groovy
java {
    sourceCompatibility = JavaVersion.VERSION_17
    targetCompatibility = JavaVersion.VERSION_17
}
```

**Adding Source Sets:**

```groovy
sourceSets {
    integrationTest {
        java.srcDir 'src/integration-test/java'
        resources.srcDir 'src/integration-test/resources'
        compileClasspath += main.output + test.output
        runtimeClasspath += main.output + test.output
    }
}
```

## Maven Central Publishing

For publishing to Maven Central, Speakeasy generates full OSSRH publishing configuration.

### Prerequisites

1. **Sonatype OSSRH Account**: Register at https://central.sonatype.org/
2. **GPG Key**: Generate a key pair and publish public key to key servers
3. **Namespace Verification**: Verify your groupID (e.g., `io.example`)

### workflow.yaml Publishing Configuration

```yaml
targets:
  my-sdk:
    target: java
    source: my-source
    output: sdk
    publish:
      java:
        ossrhUsername: $ossrh_username
        ossrhPassword: $ossrh_password
        gpgSecretKey: $java_gpg_secret_key
        gpgPassPhrase: $java_gpg_passphrase
```

### Required Secrets

| Secret | Description |
|--------|-------------|
| `OSSRH_USERNAME` | Sonatype account username |
| `OSSRH_PASSWORD` | Sonatype account password or token |
| `JAVA_GPG_SECRET_KEY` | ASCII-armored private GPG key |
| `JAVA_GPG_PASSPHRASE` | Passphrase for GPG key |

### GitHub Actions Release Workflow

Releases are typically triggered by changes to `RELEASES.md`:

```yaml
name: Release SDK
on:
  push:
    paths: [sdk/RELEASES.md]
    branches: [main]
jobs:
  publish:
    uses: speakeasy-api/sdk-generation-action/.github/workflows/sdk-publish.yaml@v15
    secrets:
      github_access_token: ${{ secrets.GITHUB_TOKEN }}
      speakeasy_api_key: ${{ secrets.SPEAKEASY_API_KEY }}
      ossrh_username: ${{ secrets.OSSRH_USERNAME }}
      ossrh_password: ${{ secrets.OSSRH_PASSWORD }}
      java_gpg_secret_key: ${{ secrets.JAVA_GPG_SECRET_KEY }}
      java_gpg_passphrase: ${{ secrets.JAVA_GPG_PASSPHRASE }}
```

### Local Development Publishing

For local testing, publish to local Maven repository:

```bash
# On macOS/Linux
./gradlew publishToMavenLocal -Pskip.signing

# On Windows
gradlew.bat publishToMavenLocal -Pskip.signing
```

### Generated build.gradle Publishing Section

The generated `build.gradle` includes full publishing configuration:

```groovy
sonatypeCentralUpload {
    username = System.getenv("SONATYPE_USERNAME")
    password = System.getenv("SONATYPE_PASSWORD")
    archives = files(
        "$buildDir/libs/${artifactId}-${version}.jar",
        "$buildDir/libs/${artifactId}-${version}-sources.jar",
        "$buildDir/libs/${artifactId}-${version}-javadoc.jar"
    )
    pom = file("$buildDir/pom.xml")
    signingKey = System.getenv("SONATYPE_SIGNING_KEY")
    signingKeyPassphrase = System.getenv("SIGNING_KEY_PASSPHRASE")
}
```

## Feature Support

### Authentication

| Method | Support | Notes |
|--------|---------|-------|
| HTTP Basic | Yes | |
| API Key (header, query, cookie) | Yes | |
| Bearer Token | Yes | |
| OAuth 2.0 Client Credentials | Yes | Via hooks |
| OAuth 2.0 Authorization Code | Yes | |

### Data Types

| Type | Support | Java Type |
|------|---------|-----------|
| string | Yes | String |
| integer (int32) | Yes | Integer |
| integer (int64) | Yes | Long |
| number (float) | Yes | Float |
| number (double) | Yes | Double |
| boolean | Yes | Boolean |
| date | Yes | LocalDate |
| date-time | Yes | OffsetDateTime |
| binary | Yes | byte[] |
| array | Yes | List<T> |
| object | Yes | Generated class |
| enum | Yes | Java enum |
| oneOf/anyOf | Yes | Union types |
| BigInteger | Yes | BigInteger |
| BigDecimal | Yes | BigDecimal |

### Methods

| Feature | Support | Notes |
|---------|---------|-------|
| Namespacing | Yes | Via tags |
| Multi-level namespacing | Yes | |
| Custom naming | Yes | x-speakeasy-name-override |
| Deprecation | Yes | @Deprecated annotation |
| Pagination | Yes | x-speakeasy-pagination |
| Retries | Yes | Configurable backoff |

### Documentation

| Feature | Support |
|---------|---------|
| README generation | Yes |
| Usage snippets | Yes |
| Per-operation docs | Yes |
| Model documentation | Yes |

## HTTP Client

The Java SDK uses Apache HttpClient 5 for HTTP requests:

```java
// Default HTTP client is created automatically
MySdk sdk = MySdk.builder()
    .security(security)
    .build();

// Custom HTTP client configuration can be provided via hooks
```

## User Agent

The Java SDK includes a user agent string in all requests:

```
speakeasy-sdk/java {SDKVersion} {GenVersion} {DocVersion} {PackageName}
```

## Dependencies

Generated Java SDKs include these core dependencies:

```groovy
dependencies {
    api 'com.fasterxml.jackson.core:jackson-annotations:2.18.2'
    implementation 'com.fasterxml.jackson.core:jackson-databind:2.18.2'
    implementation 'com.fasterxml.jackson.datatype:jackson-datatype-jsr310:2.18.2'
    implementation 'com.fasterxml.jackson.datatype:jackson-datatype-jdk8:2.18.2'
    api 'org.openapitools:jackson-databind-nullable:0.2.6'
    implementation 'org.apache.httpcomponents.client5:httpclient5:5.4.1'
    implementation 'commons-io:commons-io:2.18.0'
}
```

---

## Spring Boot Integration

### Enabling Spring Boot Starter

Speakeasy can generate a full Spring Boot auto-configuration module alongside your SDK. Add `generateSpringBootStarter: true` to `gen.yaml`:

```yaml
java:
  version: 1.0.0
  artifactID: my-sdk
  groupID: io.example
  generateSpringBootStarter: true
  languageVersion: 11   # Java 11+ required
  templateVersion: v2   # Use latest template version
```

This generates a separate Spring Boot auto-configuration module:

```
my-sdk/
├── src/main/java/io/example/    # Core SDK
└── spring/
    └── my-sdk-spring-boot-autoconfigure/
        ├── src/main/java/io/example/spring/
        │   ├── BackendApiAutoConfig.java              # Auto-configuration
        │   └── BackendApiAutoConfigProperties.java    # Configuration properties
        └── build.gradle
```

### Auto-Configuration Features

The generated auto-configuration:
- Auto-configures SDK with `@ConfigurationProperties`
- Exposes all SDK components as injectable beans
- Integrates retry, HTTP client, and security configuration
- Uses `@ConditionalOnMissingBean` for easy overrides

**Generated auto-config structure:**

```java
@AutoConfiguration
@ConditionalOnClass(MySdk.class)
@EnableConfigurationProperties(BackendApiAutoConfigProperties.class)
public class BackendApiAutoConfig {

    @Bean
    @ConditionalOnMissingBean
    public MySdk mySdk(SDKConfiguration sdkConfiguration) {
        return new MySdk(sdkConfiguration);
    }

    @Bean
    @ConditionalOnMissingBean
    public Users users(MySdk sdk) {
        return sdk.users();
    }

    @Bean
    @ConditionalOnMissingBean
    public Organizations organizations(MySdk sdk) {
        return sdk.organizations();
    }

    // All SDK sub-components exposed as beans...
}
```

### Configuration Properties

Configure the SDK via `application.properties` or `application.yml`:

```properties
# Server configuration
backendapi.server-url=https://api.example.com
backendapi.server-idx=0

# Security configuration
backendapi.security.bearer-auth=${API_SECRET_KEY}

# Retry configuration
backendapi.retry-config.strategy=BACKOFF
backendapi.retry-config.backoff.initial-interval=500
backendapi.retry-config.backoff.max-interval=60000
backendapi.retry-config.backoff.exponent=1.5
backendapi.retry-config.backoff.max-elapsed-time=3600000

# HTTP client configuration
backendapi.http-client.enable-debug-logging=false
```

Or with YAML:

```yaml
backendapi:
  server-url: https://api.example.com
  security:
    bearer-auth: ${API_SECRET_KEY}
  retry-config:
    strategy: BACKOFF
    backoff:
      initial-interval: 500
      max-interval: 60000
```

### Injecting SDK Components

With Spring Boot auto-configuration, inject SDK components directly:

```java
@Service
public class UserService {
    private final Users users;

    public UserService(Users users) {
        this.users = users;
    }

    public User getUser(String userId) {
        return users.get()
            .userId(userId)
            .call()
            .user()
            .orElseThrow(() -> new UserNotFoundException(userId));
    }

    public List<User> listUsers(int page, int pageSize) {
        return users.list()
            .page(page)
            .pageSize(pageSize)
            .call()
            .users();
    }
}
```

### Overriding Default Beans

Override any auto-configured bean with custom implementations:

```java
@Configuration
public class CustomSdkConfig {

    @Bean
    public HTTPClient httpClient() {
        // Custom HTTP client with mTLS, proxy, metrics, etc.
        return new CustomHTTPClient();
    }

    @Bean
    public RetryConfig retryConfig() {
        // Custom retry strategy
        return RetryConfig.builder()
            .maxRetries(5)
            .initialInterval(Duration.ofMillis(100))
            .build();
    }
}
```

> **Pattern Source:** Extracted from [clerk/clerk-sdk-java](https://github.com/clerk/clerk-sdk-java) - production Spring Boot integration

---

## SDK Hooks

SDK hooks enable cross-cutting concerns like API version headers, correlation IDs, logging, and custom authentication flows.

### Hook Types

| Hook | Interface | Purpose |
|------|-----------|---------|
| BeforeRequest | `BeforeRequest` | Modify requests before sending (add headers, transform payloads) |
| AfterSuccess | `AfterSuccess` | Process successful responses (logging, metrics) |
| AfterError | `AfterError` | Handle errors before throwing (transform errors, retry logic) |

### Implementing BeforeRequest Hook

Common use case: Adding API version headers to all requests.

```java
// hooks/ApiVersionHook.java
package io.example.hooks;

import io.example.utils.Helpers;
import io.example.utils.Hook.BeforeRequest;
import io.example.utils.Hook.BeforeRequestContext;
import java.net.http.HttpRequest;

public final class ApiVersionHook implements BeforeRequest {
    private final String apiVersion;

    public ApiVersionHook(String apiVersion) {
        this.apiVersion = apiVersion;
    }

    @Override
    public HttpRequest beforeRequest(BeforeRequestContext context, HttpRequest request) throws Exception {
        // Note: HttpRequest is immutable. Use Helpers.copy to create a modified copy.
        // With JDK 16+, you can use HttpRequest.newBuilder(HttpRequest, BiPredicate)
        HttpRequest.Builder b = Helpers.copy(request);
        b.header("X-API-Version", apiVersion);
        return b.build();
    }
}
```

### Correlation ID Hook

Add request correlation IDs for distributed tracing:

```java
// hooks/CorrelationIdHook.java
package io.example.hooks;

import io.example.utils.Helpers;
import io.example.utils.Hook.BeforeRequest;
import io.example.utils.Hook.BeforeRequestContext;
import java.net.http.HttpRequest;
import java.util.UUID;

public final class CorrelationIdHook implements BeforeRequest {
    @Override
    public HttpRequest beforeRequest(BeforeRequestContext context, HttpRequest request) throws Exception {
        HttpRequest.Builder b = Helpers.copy(request);
        b.header("X-Correlation-ID", UUID.randomUUID().toString());
        b.header("X-Request-ID", UUID.randomUUID().toString());
        return b.build();
    }
}
```

### Registering Hooks

Register hooks in the `SDKHooks.java` file (generated in `hooks/` directory):

```java
// hooks/SDKHooks.java
package io.example.hooks;

import io.example.utils.Hooks;

public class SDKHooks {

    public void initHooks(Hooks hooks) {
        // Register all hooks
        hooks.registerBeforeRequestHook(new ApiVersionHook("2025-01-15"));
        hooks.registerBeforeRequestHook(new CorrelationIdHook());
        hooks.registerAfterSuccessHook(new LoggingHook());
    }
}
```

### AfterSuccess Hook for Logging

```java
// hooks/LoggingHook.java
package io.example.hooks;

import io.example.utils.Hook.AfterSuccess;
import io.example.utils.Hook.AfterSuccessContext;
import java.net.http.HttpResponse;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public final class LoggingHook implements AfterSuccess {
    private static final Logger logger = LoggerFactory.getLogger(LoggingHook.class);

    @Override
    public HttpResponse<byte[]> afterSuccess(AfterSuccessContext context, HttpResponse<byte[]> response) {
        logger.info("API call completed: {} {} -> {}",
            context.request().method(),
            context.request().uri(),
            response.statusCode());
        return response;
    }
}
```

### AfterError Hook for Error Transformation

```java
// hooks/ErrorTransformHook.java
package io.example.hooks;

import io.example.utils.Hook.AfterError;
import io.example.utils.Hook.AfterErrorContext;
import java.net.http.HttpResponse;
import java.util.Optional;

public final class ErrorTransformHook implements AfterError {
    @Override
    public HttpResponse<byte[]> afterError(
            AfterErrorContext context,
            Optional<HttpResponse<byte[]>> response,
            Optional<Exception> error) throws Exception {

        if (response.isPresent() && response.get().statusCode() == 429) {
            // Log rate limiting
            logger.warn("Rate limited on {}", context.request().uri());
        }

        // Re-throw or transform the error
        if (error.isPresent()) {
            throw error.get();
        }
        return response.orElse(null);
    }
}
```

> **Pattern Source:** Extracted from [clerk/clerk-sdk-java](https://github.com/clerk/clerk-sdk-java) - API version header injection via hooks

---

## Custom Helper Code

Non-generated helper code extends SDK functionality beyond the OpenAPI spec. This is useful for authentication utilities, token verification, request signing, and domain-specific operations.

### Directory Structure

Place custom helpers in a `helpers/` package that won't be overwritten during regeneration:

```
src/main/java/io/example/
├── MySdk.java                     # Generated main class
├── models/                        # Generated models
├── utils/                         # Generated utilities
├── hooks/                         # SDK hooks (partially generated)
└── helpers/                       # Hand-written helpers (not overwritten)
    └── security/
        ├── AuthenticateRequest.java   # Request authentication
        ├── VerifyToken.java           # Token verification
        ├── Cache.java                 # JWKS caching
        ├── models/
        │   ├── AuthStatus.java        # Auth status enum
        │   ├── AuthErrorReason.java   # Error reason enum
        │   ├── RequestState.java      # Auth result container
        │   └── TokenType.java         # Token type enum
        └── token_verifiers/
            └── impl/
                ├── JwtSessionTokenVerifier.java
                ├── APIKeyTokenVerifier.java
                ├── MachineTokenVerifier.java
                └── OAuthTokenVerifier.java
```

### Request State Modeling

Model authentication results with typed states:

```java
// helpers/security/models/RequestState.java
package io.example.helpers.security.models;

import java.util.Optional;

public final class RequestState {
    private final AuthStatus status;
    private final Optional<String> token;
    private final Optional<AuthErrorReason> reason;
    private final Optional<TokenVerificationResponse<?>> verificationResponse;

    private RequestState(AuthStatus status, Optional<String> token,
                         Optional<AuthErrorReason> reason,
                         Optional<TokenVerificationResponse<?>> verificationResponse) {
        this.status = status;
        this.token = token;
        this.reason = reason;
        this.verificationResponse = verificationResponse;
    }

    public static RequestState signedIn(String token, TokenVerificationResponse<?> response) {
        return new RequestState(
            AuthStatus.SIGNED_IN,
            Optional.of(token),
            Optional.empty(),
            Optional.of(response)
        );
    }

    public static RequestState signedOut(AuthErrorReason reason) {
        return new RequestState(
            AuthStatus.SIGNED_OUT,
            Optional.empty(),
            Optional.of(reason),
            Optional.empty()
        );
    }

    public boolean isSignedIn() {
        return status == AuthStatus.SIGNED_IN;
    }

    public boolean isSignedOut() {
        return status == AuthStatus.SIGNED_OUT;
    }

    public AuthStatus status() { return status; }
    public Optional<String> token() { return token; }
    public Optional<AuthErrorReason> reason() { return reason; }
    public Optional<TokenVerificationResponse<?>> verificationResponse() { return verificationResponse; }
}
```

### Multi-Token Type Verification

Support multiple authentication token types with a dispatcher pattern:

```java
// helpers/security/VerifyToken.java
package io.example.helpers.security;

import io.example.helpers.security.models.*;
import io.example.helpers.security.token_verifiers.impl.*;
import java.io.IOException;

public final class VerifyToken {

    private VerifyToken() {
        // Utility class
    }

    public static TokenVerificationResponse<?> verifyToken(String token, VerifyTokenOptions options)
            throws TokenVerificationException, IOException, InterruptedException {

        TokenType tokenType = getTokenType(token);

        switch (tokenType) {
            case API_KEY:
                return new APIKeyTokenVerifier().verify(token, options);
            case MACHINE_TOKEN:
                return new MachineTokenVerifier().verify(token, options);
            case OAUTH_TOKEN:
                return new OAuthTokenVerifier().verify(token, options);
            case SESSION_TOKEN:
            default:
                return JwtSessionTokenVerifier.verify(token, options);
        }
    }

    private static TokenType getTokenType(String token) {
        if (token.startsWith("ak_")) return TokenType.API_KEY;
        if (token.startsWith("mt_")) return TokenType.MACHINE_TOKEN;
        if (token.startsWith("oat_")) return TokenType.OAUTH_TOKEN;
        return TokenType.SESSION_TOKEN;
    }
}
```

### Request Authentication Entry Point

```java
// helpers/security/AuthenticateRequest.java
package io.example.helpers.security;

import io.example.helpers.security.models.*;
import java.io.IOException;
import java.util.*;

public final class AuthenticateRequest {

    private static final String SESSION_COOKIE_NAME = "__session";

    private AuthenticateRequest() {
        // Utility class
    }

    public static RequestState authenticateRequest(
            Map<String, List<String>> requestHeaders,
            AuthenticateRequestOptions options) {

        String token = extractToken(requestHeaders);
        if (token == null) {
            return RequestState.signedOut(AuthErrorReason.SESSION_TOKEN_MISSING);
        }

        TokenType tokenType = getTokenType(token);
        List<String> acceptedTokens = options.acceptsToken();

        if (!acceptedTokens.contains(tokenType.getType()) && !acceptedTokens.contains("any")) {
            return RequestState.signedOut(AuthErrorReason.TOKEN_TYPE_NOT_SUPPORTED);
        }

        try {
            VerifyTokenOptions verifyOptions = buildVerifyTokenOptions(options);
            TokenVerificationResponse<?> response = VerifyToken.verifyToken(token, verifyOptions);
            return RequestState.signedIn(token, response);
        } catch (TokenVerificationException e) {
            return RequestState.signedOut(e.reason());
        } catch (IOException | InterruptedException e) {
            return RequestState.signedOut(AuthErrorReason.INTERNAL_ERROR);
        }
    }

    private static String extractToken(Map<String, List<String>> headers) {
        // Normalize headers to lowercase
        Map<String, List<String>> normalized = new HashMap<>();
        headers.forEach((k, v) -> normalized.put(k.toLowerCase(), v));

        // Check Authorization header first
        List<String> authHeaders = normalized.get("authorization");
        if (authHeaders != null && !authHeaders.isEmpty()) {
            String bearer = authHeaders.get(0);
            return bearer.replace("Bearer ", "");
        }

        // Fall back to session cookie
        List<String> cookieHeaders = normalized.get("cookie");
        if (cookieHeaders == null || cookieHeaders.isEmpty()) {
            return null;
        }

        return Arrays.stream(cookieHeaders.get(0).split(";"))
            .map(String::trim)
            .map(s -> s.split("=", 2))
            .filter(kv -> kv[0].equals(SESSION_COOKIE_NAME))
            .map(kv -> kv[1])
            .findFirst()
            .orElse(null);
    }
}
```

### Testing Custom Helpers

Use Mockito for testing custom helpers with mocked dependencies:

```java
// src/test/java/io/example/helpers/security/AuthenticateRequestTest.java
package io.example.helpers.security;

import io.example.helpers.security.models.*;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.mockito.*;
import java.util.*;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.Mockito.*;

public class AuthenticateRequestTest {

    @Mock
    private AuthenticateRequestOptions options;

    @BeforeEach
    public void setUp() {
        MockitoAnnotations.openMocks(this);
        when(options.jwtKey()).thenReturn(Optional.empty());
        when(options.secretKey()).thenReturn(Optional.empty());
        when(options.audience()).thenReturn(Optional.of("test"));
        when(options.authorizedParties()).thenReturn(Collections.emptySet());
        when(options.clockSkewInMs()).thenReturn(0L);
    }

    @Test
    public void testMissingToken() {
        Map<String, List<String>> headers = new HashMap<>();
        RequestState result = AuthenticateRequest.authenticateRequest(headers, options);

        assertFalse(result.isSignedIn());
        assertEquals(AuthErrorReason.SESSION_TOKEN_MISSING, result.reason().get());
    }

    @Test
    public void testValidBearerToken() {
        Map<String, List<String>> headers = new HashMap<>();
        when(options.acceptsToken()).thenReturn(List.of("session_token"));
        headers.put("authorization", Collections.singletonList("Bearer test-token"));

        TokenVerificationResponse<?> mockResponse = mock(TokenVerificationResponse.class);

        try (MockedStatic<VerifyToken> mocked = mockStatic(VerifyToken.class)) {
            mocked.when(() -> VerifyToken.verifyToken(eq("test-token"), any()))
                .thenReturn(mockResponse);

            RequestState result = AuthenticateRequest.authenticateRequest(headers, options);

            assertTrue(result.isSignedIn());
            assertEquals("test-token", result.token().get());
        }
    }

    @Test
    public void testUnsupportedTokenType() {
        when(options.acceptsToken()).thenReturn(List.of("machine_token", "api_key"));
        Map<String, List<String>> headers = new HashMap<>();
        headers.put("authorization", Collections.singletonList("Bearer unsupported-token"));

        RequestState result = AuthenticateRequest.authenticateRequest(headers, options);

        assertTrue(result.isSignedOut());
        assertEquals(AuthErrorReason.TOKEN_TYPE_NOT_SUPPORTED, result.reason().get());
    }
}
```

> **Pattern Source:** Extracted from [clerk/clerk-sdk-java](https://github.com/clerk/clerk-sdk-java) - comprehensive multi-token authentication helpers

---

## Pre-defined TODO List

When generating a Java SDK, initialize your TODO list with:

| Step | TODO Item | Active Form |
|------|-----------|-------------|
| 1 | Configure gen.yaml for Java target | Configuring gen.yaml for Java target |
| 2 | Set groupID, artifactID, and version | Setting Maven coordinates |
| 3 | Configure sdkClassName | Configuring SDK class name |
| 4 | Set maxMethodParams | Setting maxMethodParams |
| 5 | Enable Spring Boot starter if needed | Enabling Spring Boot starter |
| 6 | Generate SDK with speakeasy run | Generating SDK |
| 7 | Verify SDK compilation (./gradlew build) | Verifying SDK compilation |
| 8 | Create build-extras.gradle for customizations | Creating build customizations |
| 9 | Implement SDK hooks if needed | Implementing SDK hooks |
| 10 | Add custom helper code if needed | Adding custom helper code |
| 11 | Configure publishing secrets | Configuring publishing secrets |
| 12 | Test local Maven publishing | Testing local publishing |
| 13 | Set up CI/CD release workflow | Setting up release workflow |

**Usage:**
```
TodoWrite([
  {content: "Configure gen.yaml for Java target", status: "pending", activeForm: "Configuring gen.yaml for Java target"},
  {content: "Set groupID, artifactID, and version", status: "pending", activeForm: "Setting Maven coordinates"},
  {content: "Configure sdkClassName", status: "pending", activeForm: "Configuring SDK class name"},
  {content: "Set maxMethodParams", status: "pending", activeForm: "Setting maxMethodParams"},
  {content: "Enable Spring Boot starter if needed", status: "pending", activeForm: "Enabling Spring Boot starter"},
  {content: "Generate SDK with speakeasy run", status: "pending", activeForm: "Generating SDK"},
  {content: "Verify SDK compilation (./gradlew build)", status: "pending", activeForm: "Verifying SDK compilation"},
  {content: "Create build-extras.gradle for customizations", status: "pending", activeForm: "Creating build customizations"},
  {content: "Implement SDK hooks if needed", status: "pending", activeForm: "Implementing SDK hooks"},
  {content: "Add custom helper code if needed", status: "pending", activeForm: "Adding custom helper code"},
  {content: "Configure publishing secrets", status: "pending", activeForm: "Configuring publishing secrets"},
  {content: "Test local Maven publishing", status: "pending", activeForm: "Testing local publishing"},
  {content: "Set up CI/CD release workflow", status: "pending", activeForm: "Setting up release workflow"}
])
```

**Nested workflows:**
- See `plans/sdk-generation.md` for the full SDK generation workflow
- See `spec-first/validation.md` for OpenAPI validation before generation

**Conditional steps:**
- Step 5 (Spring Boot starter): Only applicable for Spring Boot applications
- Step 9 (SDK hooks): For API version headers, correlation IDs, logging, etc.
- Step 10 (Custom helpers): For authentication utilities, token verification, etc.
