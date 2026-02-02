---
name: generate-sdk-for-java
description: >-
  Use when generating a Java SDK with Speakeasy. Covers gen.yaml configuration,
  Gradle/Maven setup, builder patterns, Maven Central publishing.
  Triggers on "Java SDK", "generate Java", "Maven Central", "Gradle SDK",
  "Java client library".
license: Apache-2.0
---

# Generate SDK for Java

Configure and generate idiomatic Java SDKs with Speakeasy, featuring builder patterns, Jackson serialization, and Maven Central publishing.

## When to Use

- Generating a new Java SDK from an OpenAPI spec
- Configuring Java-specific gen.yaml options
- Setting up Gradle or Maven builds
- Publishing to Maven Central
- User says: "Java SDK", "Maven Central", "Gradle", "Java client"

## Quick Start

```bash
speakeasy quickstart --skip-interactive --output console \
  -s openapi.yaml -t java -n "MySDK" -p "com.myorg.mysdk"
```

## Essential gen.yaml Configuration

```yaml
java:
  version: 1.0.0
  groupID: com.myorg
  artifactID: my-sdk
  packageName: com.myorg.mysdk

  # Method signatures
  maxMethodParams: 4
  methodArguments: require-security-and-request

  # Response handling
  responseFormat: flat
  clientServerStatusCodesAsErrors: true
```

## Package Structure

```
├── src/main/java/com/myorg/mysdk/
│   ├── MySdk.java           # Main SDK class
│   ├── *.java               # Operation classes
│   ├── models/
│   │   ├── shared/          # Component types
│   │   ├── operations/      # Request/response types
│   │   └── errors/          # Error types
│   └── utils/               # Internal utilities
├── build.gradle
├── build-extras.gradle      # Custom build config (preserved)
└── settings.gradle
```

## Client Usage

Java SDKs use builder patterns:

```java
import com.myorg.mysdk.MySdk;
import com.myorg.mysdk.models.shared.*;

// Build client
MySdk sdk = MySdk.builder()
    .security(Security.builder()
        .apiKey("your-api-key")
        .build())
    .build();

// Make API call
CreateResponse response = sdk.resources().create()
    .request(CreateRequest.builder()
        .name("my-resource")
        .build())
    .call();

if (response.resource().isPresent()) {
    System.out.println(response.resource().get().id());
}
```

## Build Customization

Use `build-extras.gradle` for custom build config (preserved across regeneration):

```gradle
// build-extras.gradle
dependencies {
    implementation 'org.slf4j:slf4j-api:2.0.9'
}

tasks.withType(JavaCompile) {
    options.compilerArgs << '-Xlint:deprecation'
}
```

## Maven Central Publishing

1. Configure in gen.yaml:
```yaml
java:
  groupID: com.myorg
  artifactID: my-sdk
  version: 1.0.0
```

2. Set up signing and credentials in `gradle.properties`

3. Publish:
```bash
./gradlew publishToSonatype closeAndReleaseSonatypeStagingRepository
```

## Common Configuration Options

| Option | Default | Description |
|--------|---------|-------------|
| `groupID` | io.github | Maven group ID |
| `artifactID` | openapi | Maven artifact ID |
| `maxMethodParams` | 0 | Max params before request object |

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Build fails | Check Java 11+ is installed |
| Missing Optional | Use `.isPresent()` and `.get()` |
| Gradle sync fails | Run `./gradlew --refresh-dependencies` |

## Related Skills

- `start-new-sdk-project` - Initial SDK setup
- `customize-sdk-hooks` - Hook implementation
- `setup-sdk-testing` - Testing patterns
- `manage-openapi-overlays` - Spec customization
