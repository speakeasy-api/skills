# Java SDK Configuration

Detailed gen.yaml configuration options for Java SDKs.

## gen.yaml Configuration

```yaml
java:
  version: 1.0.0
  groupID: com.myorg
  artifactID: my-sdk
  packageName: com.myorg.mysdk

  # Method signatures
  methodArguments: require-security-and-request
  maxMethodParams: 4
```

## Package Structure

```
my-sdk/
├── build.gradle
├── build-extras.gradle      # Custom build config (preserved)
├── settings.gradle
├── src/
│   └── main/
│       └── java/
│           └── com/myorg/mysdk/
│               ├── SDK.java         # Main SDK class
│               ├── models/
│               │   ├── operations/  # Request/response
│               │   ├── shared/      # Shared models
│               │   └── errors/      # Error classes
│               └── hooks/           # Custom hooks (preserved)
│                   └── HookRegistration.java
└── docs/
```

## Builder Pattern

All SDK classes use the builder pattern:

```java
import com.myorg.mysdk.SDK;
import com.myorg.mysdk.models.shared.Security;

SDK sdk = SDK.builder()
    .security(Security.builder()
        .apiKey("your-api-key")
        .build())
    .build();

// Create user with builder
CreateUserRequest request = CreateUserRequest.builder()
    .name("Alice")
    .email("alice@example.com")
    .build();

User user = sdk.users().create(request);
```

## Security Configuration

```java
// API Key
SDK sdk = SDK.builder()
    .security(Security.builder()
        .apiKey("your-api-key")
        .build())
    .build();

// Bearer Token
SDK sdk = SDK.builder()
    .security(Security.builder()
        .bearerAuth("your-token")
        .build())
    .build();

// OAuth2
SDK sdk = SDK.builder()
    .security(Security.builder()
        .oauth2("your-oauth-token")
        .build())
    .build();
```

## Server Selection

```java
// Named server from spec
SDK sdk = SDK.builder()
    .server(Server.PRODUCTION)
    .build();

// Custom URL
SDK sdk = SDK.builder()
    .serverURL("https://api.example.com")
    .build();
```

## Error Handling

```java
import com.myorg.mysdk.models.errors.APIException;
import com.myorg.mysdk.models.errors.SDKException;

try {
    User user = sdk.users().get("invalid-id");
} catch (APIException e) {
    // Server returned error status
    System.out.println("Status: " + e.getStatusCode());
    System.out.println("Body: " + e.getBody());
} catch (SDKException e) {
    // Network, timeout, or other SDK error
    System.out.println("SDK error: " + e.getMessage());
}
```

## Retries Configuration

```java
import com.myorg.mysdk.utils.RetryConfig;
import com.myorg.mysdk.utils.BackoffStrategy;

SDK sdk = SDK.builder()
    .retryConfig(RetryConfig.builder()
        .strategy("backoff")
        .backoff(BackoffStrategy.builder()
            .initialInterval(500)
            .maxInterval(60000)
            .exponent(1.5)
            .maxElapsedTime(300000)
            .build())
        .retryConnectionErrors(true)
        .build())
    .build();
```

## Timeouts

```java
// Global timeout
SDK sdk = SDK.builder()
    .timeoutMs(30000)
    .build();

// Per-call override (using options)
User user = sdk.users().create(request,
    CreateUserRequestOptions.builder()
        .timeoutMs(60000)
        .build());
```

## Pagination

```java
// Auto-iterate all pages
ListUsersResponse response = sdk.users().list(
    ListUsersRequest.builder().limit(50).build());

for (User user : response) {
    System.out.println(user.getName());
}

// Manual pagination
ListUsersResponse page = sdk.users().list(
    ListUsersRequest.builder().limit(50).build());

while (page != null) {
    for (User user : page.getUsers()) {
        System.out.println(user.getName());
    }
    page = page.next();
}
```

## Custom Build Configuration

Edit `build-extras.gradle` for custom dependencies or tasks (preserved on regeneration):

```groovy
// build-extras.gradle
dependencies {
    implementation 'com.google.code.gson:gson:2.10.1'
    testImplementation 'org.mockito:mockito-core:5.0.0'
}

tasks.register('customTask') {
    doLast {
        println 'Custom build task'
    }
}
```

## Custom Hooks

Create hooks in `src/main/java/com/myorg/mysdk/hooks/`:

```java
package com.myorg.mysdk.hooks;

import java.net.http.HttpRequest;
import java.net.http.HttpResponse;

public class HookRegistration {
    public static void initHooks(Hooks hooks) {
        hooks.beforeRequest(request -> {
            return HttpRequest.newBuilder(request, (n, v) -> true)
                .header("X-Custom-Header", "value")
                .build();
        });

        hooks.afterResponse((response, request) -> {
            System.out.printf("%s %s: %d%n",
                request.method(),
                request.uri(),
                response.statusCode());
            return response;
        });

        hooks.onError((error, request) -> {
            System.err.println("Error: " + error.getMessage());
            throw error;
        });
    }
}
```

## Async Operations

Java SDK operations are synchronous by default. For async:

```java
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

ExecutorService executor = Executors.newCachedThreadPool();

CompletableFuture<User> future = CompletableFuture.supplyAsync(() ->
    sdk.users().get("123"), executor);

future.thenAccept(user -> {
    System.out.println(user.getName());
});
```

## Publishing to Maven Central

### Prerequisites

1. Create Sonatype OSSRH account
2. Configure GPG signing
3. Set credentials in `~/.gradle/gradle.properties`:

```properties
ossrhUsername=your-username
ossrhPassword=your-password
signing.keyId=your-key-id
signing.password=your-key-password
signing.secretKeyRingFile=/path/to/.gnupg/secring.gpg
```

### Publish

```bash
./gradlew publishToSonatype closeAndReleaseSonatypeStagingRepository
```

## Debugging

```java
import java.util.logging.Logger;
import java.util.logging.Level;

// Enable SDK logging
Logger.getLogger("com.myorg.mysdk").setLevel(Level.FINE);

// Or use custom logger
SDK sdk = SDK.builder()
    .logger(myCustomLogger)
    .build();
```

## Common Issues

| Issue | Solution |
|-------|----------|
| Gradle sync fails | Run `./gradlew --refresh-dependencies` |
| SSL errors | Configure custom `SSLContext` |
| Jackson serialization | Check `@JsonProperty` annotations match spec |
| Thread safety | SDK instances are thread-safe |
| Memory leaks | Close HTTP client: `sdk.close()` |
