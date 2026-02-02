---
short_description: "TypeScript SDK generation guide"
long_description: |
  Comprehensive guide for generating TypeScript SDKs with Speakeasy.
  Includes methodology, feature support, OSS comparison, dependency management,
  standalone functions, migration guide, and language-specific configuration.
source:
  - repo: "speakeasy-api/speakeasy.com"
    path: "src/content/docs/sdks/languages/typescript/"
    ref: "af7c36a9ec957336fb799151a4e5af3ae293831e"
    last_reconciled: "2025-12-11"
  - repo: "speakeasy-sdks/visa-payments-typescript-sdk"
    path: ".speakeasy/gen.yaml"
    ref: "main"
    last_reconciled: "2025-12-11"
    notes: "additionalDependencies for crypto-js pattern"
---

# TypeScript SDK Generation

## SDK Overview

The Speakeasy TypeScript SDK creation builds idiomatic TypeScript libraries using standard web platform features.

The SDK is strongly typed, makes minimal use of third-party modules, and is straightforward to debug. Using the SDKs that Speakeasy generates will feel familiar to TypeScript developers. We make opinionated choices in some places but do so thoughtfully and deliberately.

The core features of the TypeScript SDK include:

- Compatibility with vanilla JavaScript projects since the SDK's consumption is through `.d.ts` (TypeScript type definitions) and `.js` files.
- Usable on the server and in the browser.
- Use of the `fetch`, `ReadableStream`, and async iterable APIs for compatibility with popular JavaScript runtimes:
  - Node.js
  - Deno
  - Bun
- Support for streaming requests and responses.
- Authentication support for OAuth flows and support for standard security mechanisms (HTTP Basic, application tokens, and so on).
- Optional pagination support for supported APIs.
- Optional support for retries in every operation.
- Complex number types including big integers and decimals.
- Date and date/time types using RFC3339 date formats.
- Custom type enums using strings and integers.
- Union types and combined types.

## TypeScript Package Structure

```
src/
  lib/
    ...
    http.ts
    sdks.ts
    ...
  sdk/
    models/
      errors/
        ...
      operations/
        ...
      shared/
        ...
    types/
      ...
    index.ts
    sdk.ts
    ...
  index.ts
docs/
  ...
...
```

## Runtime Environment Requirements

The SDK targets ES2018, ensuring compatibility with a wide range of JavaScript runtimes that support this version. Key features required by the SDK include:

- Web Fetch API
- Web Streams API and in particular `ReadableStream`
- Async iterables using `Symbol.asyncIterator`

> **Note:** We used data from `caniuse` and `mdn` to determine our support policy and when we adopt a javascript feature. Typically we adopt features that have been out for > 3 years with reasonable support.

Runtime environments that are explicitly supported are:

- Evergreen browsers: Chrome, Safari, Edge, Firefox.
- Node.js active and maintenance LTS releases (currently, v18 and v20).
- Bun v1 and above.
- Deno v1.39 - Note Deno doesn't currently have native support for streaming file uploads backed by the filesystem.

> **Note:** For teams interested in working directly with the SDK's source files, our SDK leverages TypeScript `v5` features. To directly consume these source files, your environment should support TypeScript version 5 or higher. This requirement applies to scenarios where direct access to the source is necessary.

## TypeScript HTTP Client

TypeScript SDKs stick as close to modern and ubiquitous web standards as possible. We use the `fetch()` API as our HTTP client. The API includes all the necessary building blocks to make HTTP requests: `fetch`, `Request`, `Response`, `Headers`, `FormData`, `File`, and `Blob`.

The standard nature of this SDK ensures it works in modern JavaScript runtimes, including Node.js, Deno, Bun, and React Native. We've run our extensive suite to confirm that new SDKs work in Node.js, Bun, and browsers.

## Type System

### Primitive Types

Where possible the TypeScript SDK uses primitive types such as `string`, `number`, and `boolean`. In the case of arbitrary-precision decimals, a third-party library is used since there isn't a native decimal type. Using decimal types is crucial in certain applications such as code manipulating monetary amounts and in situations where overflow, underflow, or truncation caused by precision loss can lead to significant incidents.

To describe a decimal type in OpenAPI, use the `format: decimal` keyword. The SDK will take care of serializing and deserializing decimal values under the hood using the decimal.js library.

```typescript
import { SDK } from "@speakeasy/super-sdk";
import { Decimal } from "@speakeasy/super-sdk/types";

const sdk = new SDK();
const result = await sdk.payments.create({
  amount: new Decimal(0.1).add(new Decimal(0.2)),
});
```

Similar to decimal types, we've introduced support for native `BigInt` values for numbers too large to be represented using the JavaScript `Number` type.

In an OpenAPI schema, fields for big integers can be modeled as strings with `format: bigint`.

```typescript
import { SDK } from "@speakeasy/super-sdk";

const sdk = new SDK();
const result = await sdk.doTheThing({
  value: 67_818_454n,
  value: BigInt("340656901"),
});
```

### Generated Types

The TypeScript SDK generates a type for each request, response, and shared model in your OpenAPI schema. Each model is backed by a Zod schema that validates the objects at runtime.

> **Note:** It's important to note that data validation is run on user input when calling an SDK method and on the subsequent response data from the server. If servers are not returning data that matches the OpenAPI spec, then validation errors are thrown at runtime.

### Model Structure Overview

#### Public Type

The public type represents the model that SDK users will work with inside their code.

```typescript
export type DrinkOrder = {
  id: string;
  type: DrinkType;
  customer: Customer;
  totalCost: Decimal$ | number;
  createdAt: Date;
};
```

#### Internal Types

A special namespace accompanies every model and contains the types and schemas for the model that represent inbound and outbound data.

> **Note:** The namespace, including types and values in it, isn't intended for use outside the SDK and is marked as `@internal`.

```typescript
/** @internal */
export namespace DrinkOrder$ {
```

#### Inbound

The inbound representation of a model defines the shape of the data received from a server. It is validated and deserialized into the public type above.

```typescript
  export type Inbound = {
    id: string;
    type: DrinkType;
    customer: Customer$.Inbound;
    total_cost: string;
    created_at: string;
  };

  export const inboundSchema: z.ZodType<DrinkOrder, z.ZodTypeDef, Inbound> = z
    .object({
      id: z.string(),
      type: DrinkType$,
      customer: Customer$.inboundSchema,
      total_cost: z.string().transform((v) => new Decimal$(v)),
      created_at: z
        .string()
        .datetime({ offset: true })
        .transform((v) => new Date(v)),
    })
    .transform((v) => {
      return {
        id: v.id,
        type: v.type,
        customer: v.customer,
        totalCost: v.total_cost,
        createdAt: v.created_at,
      };
    });
```

#### Outbound

The outbound representation of a model defines the shape of the data sent to a server. A user provides a value that satisfies the public type above and the outbound schema serializes it into what the server expects.

```typescript
  export type Outbound = {
    id: string;
    type: DrinkType;
    customer: Customer$.Outbound;
    total_cost: string;
    created_at: string;
  };

  export const outboundSchema: z.ZodType<Outbound, z.ZodTypeDef, DrinkOrder> = z
    .object({
      id: z.string(),
      type: DrinkType$,
      customer: Customer$.outboundSchema,
      totalCost: z
        .union([z.instanceof(Decimal$), z.number()])
        .transform((v) => `${v}`),
      createdAt: z.date().transform((v) => v.toISOString()),
    })
    .transform((v) => {
      return {
        id: v.id,
        type: v.type,
        customer: v.customer,
        total_cost: v.totalCost,
        created_at: v.createdAt,
      };
    });
```

### Zod Validation

All generated models have this overall structure. By pinning the types with runtime validation, Speakeasy gives users a stronger guarantee that the SDK types they work with during development are valid at runtime, otherwise, Speakeasy throws exceptions that fail loudly.

> **Note:** Zod is bundled as a regular dependency (not a peer dependency) in Speakeasy TypeScript SDKs. This ensures the SDK always uses its own bundled Zod even if the consumer app uses a different Zod version, preventing version conflicts. Speakeasy SDKs wrap `ZodError`s with a custom error type declared in each SDK. In practice, the Zod error is hidden from users who only work with the error type exported from the SDK.

### Union Types

Support for polymorphic types is critical to most production applications. In OpenAPI, these types are defined using the `oneOf` keyword. Speakeasy represents these types using TypeScript's union notation, for example, `Cat | Dog`.

```typescript
import { SDK } from "@speakeasy/super-sdk";

async function run() {
  const sdk = new SDK();
  const pet = await sdk.fetchMyPet();

  switch (pet.type) {
    case "cat":
      console.log(pet.litterType);
      break;
    case "dog":
      console.log(pet.favoriteToy);
      break;
    default:
      // Ensures exhaustive switch statements in TypeScript
      pet satisfies never;
      throw new Error(`Unidentified pet type: ${pet.type}`);
  }
}

run();
```

### Type Safety

TypeScript provides static type safety to give you greater confidence in the code you are shipping. However, TypeScript has limited support to protect from opaque data at the boundaries of your programs. User input and server data coming across the network can circumvent static typing if not correctly modeled. This usually means marking this data as `unknown` and exhaustively sanitizing it.

Our TypeScript SDKs solve this issue neatly by modeling all the data at the boundaries using Zod schemas. Using Zod schemas ensures that everything coming from users and servers will work as intended, or fail loudly with clear validation errors. This is even more impactful for the vanilla JavaScript developers using your SDK.

```typescript
import { SDK } from "@speakeasy/super-sdk";

async function run() {
  const sdk = new SDK();

  const result = await sdk.products.create({
    name: "Fancy pants",
    price: "ummm",
  });
}

run();

// Throws ZodError with validation details
```

While validating user input is considered table stakes for SDKs, it's especially useful to validate server data given the information we have in your OpenAPI spec. This can help detect drift between schema and server and prevent certain runtime issues such as missing response fields or sending incorrect data types.

## Tree Shaking

Speakeasy-created Typescript SDKs contain few internal couplings between modules. Users who bundle them into client-side apps can take advantage of tree-shaking performance when working with "deep" SDKs. These SDKs are subdivided into namespaces like `sdk.comments.create(...)` and `sdk.posts.get(...)`. Importing the top-level SDK pulls the entire SDK into a client-side bundle even if a small subset of functionality was needed.

You can import the exact namespaces or "sub-SDKs", and tree-shake the rest of the SDK away at build time.

```typescript
import { PaymentsSDK } from "@speakeasy/super-sdk/sdk/payments";

// Only code needed by this SDK is pulled in by bundlers

async function run() {
  const payments = new PaymentsSDK({ authKey: "" });

  const result = await payments.list();

  console.log(result);
}

run();
```

Speakeasy benchmarked whether there would be benefits in allowing users to import individual SDK operations but from our testing, there was a marginal reduction in bundled code versus importing sub-SDKs. It's highly dependent on how operations are grouped and the depth and breadth of an SDK as defined in the OpenAPI spec.

## Streaming Support

Support for streaming is critical for applications that need to send or receive large amounts of data between client and server without first buffering the data into memory, potentially exhausting this system resource. Uploading a huge file is one use case where streaming can be useful.

As an example, in Node.js v20, streaming a large file to a server using an SDK is only a handful of lines:

```typescript
import { openAsBlob } from "node:fs";
import { SDK } from "@speakeasy/super-sdk";

async function run() {
  const sdk = new SDK();

  const fileHandle = await openAsBlob("./src/sample.txt");

  const result = await sdk.upload({ file: fileHandle });

  console.log(result);
}
run();
```

In the browser, users would typically select files using `<input type="file">` and the SDK call is identical to the sample code above.

For response streaming, SDKs expose a `ReadableStream`, a part of the Streams API web standard.

```typescript
import fs from "node:fs";
import { Writable } from "node:stream";
import { SDK } from "@speakeasy/super-sdk";

async function run() {
  const sdk = new SDK();

  const result = await sdk.usageReports.download("UR123");

  const destination = Writable.toWeb(fs.createWriteStream("./report.csv"));

  await result.data.pipeTo(destination);
}

run();
```

## Server-Sent Events

TypeScript SDKs support the streaming of server-sent events by exposing async iterables. Unlike the native `EventSource` API, SDKs can create streams using GET or POST requests, and other methods that can pass custom headers and request bodies.

```typescript
import { SDK } from "@speakeasy/super-sdk";

async function run() {
  const sdk = new SDK();

  const result = await sdk.completions.chat({
    messages: [
      {
        role: "user",
        content: "What is the fastest bird that is common in North America?",
      },
    ],
  });

  if (result.chatStream == null) {
    throw new Error("failed to create stream: received null value");
  }

  for await (const event of result.chatStream) {
    process.stdout.write(event.data.content);
  }
}

run();
```

## Standalone Functions

Every method in TypeScript SDKs generated by Speakeasy is also available as a standalone function. This alternative API is ideal for browser or serverless environments, where bundlers can optimize applications by tree-shaking unused functionality. This includes unused methods, Zod schemas, encoding helpers, and response handlers. As a result, the application's final bundle size is dramatically smaller and grows very gradually as more of the generated SDK is used.

Using methods through the main SDK class remains a valid and generally more ergonomic option. Standalone functions are an optimization designed for specific types of applications.

### Usage

**Step 1: Import the Core Class and Function**

```typescript
import { TodoCore } from "todo/core.js";
import { todosCreate } from "todo/funcs/todosCreate.js";
```

The `Core` SDK class is optimized for tree-shaking, and can be reused throughout the application.

**Step 2: Instantiate the Core Class**

```typescript
const todoSDK = new TodoCore({
  apiKey: "TODO_API_KEY",
});
```

**Step 3: Call the Standalone Function & Handle the Result**

Invoke the standalone function, passing the core instance the first parameter. Handle the result using a switch statement for comprehensive error handling:

```typescript
async function run() {
  const res = await todosCreate(todoSDK);

  switch (true) {
    case res.ok:
      // Successful response is processed later.
      break;
    case res.error instanceof SDKValidationError:
      // Display validation errors in a readable format.
      return console.log(res.error.pretty());
    case res.error instanceof Error:
      // Handle general errors.
      return console.log(res.error);
    default:
      // Ensure all error cases are exhaustively handled.
      res.error satisfies never;
      throw new Error("Unexpected error case: " + res.error);
  }

  const { value: todo } = res;

  // Handle the successful result.
  console.log(todo);
}

run();
```

### Result Types

Standalone functions differ from SDK methods in that they return a `Result<Value, Error>` type to capture known errors and document them through the type system. This approach avoids throwing errors, allowing application code to maintain clear control flow while making error handling a natural part of the application code.

> **Note:** The term "known errors" is used because standalone functions and JavaScript code can still throw unexpected errors (e.g., `TypeError`, `RangeError`, and `DOMException`). While exhaustively catching all errors may be addressed in future SDK versions, there's significant value in capturing most errors and converting them into values.

Another reason for this programming style is that these functions are commonly used in front-end applications where throwing exceptions is often discouraged. React and similar frameworks promote this approach to ensure components can render appropriate content in all states—loading, success, and error.

## Parameters

If configured, Speakeasy generates methods with parameters for each parameter defined in the OpenAPI document, provided the number of parameters is less than or equal to the configured `maxMethodParams` value in the `gen.yaml` file.

If the number of parameters exceeds the configured `maxMethodParams` value or is set to `0`, then a request object is generated for the method instead allowing all parameters to be passed in a single object.

## Errors

Following TypeScript best practices, all operation methods in the SDK will return a response object and an error. Callers should always check for the presence of the error. The object used for errors is configurable per request. Any error response may return a custom error object. A generic error will be provided when any sort of communication failure is detected during an operation.

Here's an example of custom error handling:

```typescript
import { Speakeasy } from "@speakeasy/bar";
import * as errors from "@speakeasy/bar/sdk/models/errors";

async function run() {
  const sdk = new Speakeasy({
    apiKey: "<YOUR_API_KEY_HERE>",
  });

  const res = await sdk.bar.getDrink().catch((err) => {
    if (err instanceof errors.FailResponse) {
      console.error(err); // handle exception
      return null;
    } else {
      throw err;
    }
  });

  if (res?.statusCode !== 200) {
    throw new Error("Unexpected status code: " + res?.statusCode || "-");
  }

  // handle response
}

run();
```

The SDK also includes a `SDKValidationError` to make it easier to debug validation errors, particularly when the server sends unexpected data. Instead of throwing a `ZodError` back at SDK users without revealing the underlying raw data that failed validation, `SDKValidationError` provides a way to pretty-print validation errors for a more pleasant debugging experience.

### ResponseValidationError

A `ResponseValidationError` (a type of `SDKValidationError`) occurs when the server returns a **successful response** (2xx status) but the response body doesn't match the SDK's expected types. This typically indicates a mismatch between the OpenAPI spec and the actual API implementation.

```typescript
import { SDK } from "your-sdk";
import { ResponseValidationError } from "your-sdk/sdk/models/errors";

async function run() {
  const sdk = new SDK({ apiKey: "<YOUR_API_KEY>" });

  try {
    const res = await sdk.resources.get({ id: "123" });
    console.log(res);
  } catch (err) {
    if (err instanceof ResponseValidationError) {
      // Server returned 200 OK, but response doesn't match expected schema
      // This is a spec/API mismatch, not an API error
      console.error("Type mismatch:", err.message);
      console.error("Raw response:", err.rawValue);
    } else {
      throw err;
    }
  }
}
```

**Common causes of ResponseValidationError:**
- API returns a field not defined in the spec
- API returns a different type than expected (e.g., string instead of number)
- API returns `null` for a field not marked `nullable`
- API returns an enum value not listed in the spec

**If you encounter ResponseValidationError:**
1. Use contract testing to systematically identify all type mismatches: `../sdk-testing/contract-testing.md`
2. Update the OpenAPI spec or create an overlay to fix the types
3. Regenerate the SDK with `speakeasy run`

> **See also:** `../spec-first/validation.md#dynamic-validation-contract-testing` for the validation workflow.

## Debugging Support

Typescript SDKs support a new response format that includes the native Request and Response objects that were used in an SDK method call. Enable this by setting the `responseFormat` config in your `gen.yaml` file to `envelope-http`.

```typescript
const sdk = new SDK();
const { users, httpMeta } = await sdk.users.list();

const { request, response } = httpMeta;
console.group("Request completed");
console.log("Endpoint:", request.method, request.url);
console.log("Status", response.status);
console.log("Content type", response.headers.get("content-type"));
console.groupEnd();
```

The `httpMeta` property will also be available on any error class that relates to HTTP requests. This includes the built-in `SDKError` class and any custom error classes that you have defined in your spec.

## User Agent Strings

The Typescript SDK includes a User-Agent string in all requests to track SDK usage amongst broader API usage. The format is as follows:

```
speakeasy-sdk/typescript {{SDKVersion}} {{GenVersion}} {{DocVersion}} {{PackageName}}
```

Where

- `SDKVersion` is the version of the SDK, defined in `gen.yaml` and released.
- `GenVersion` is the version of the Speakeasy generator.
- `DocVersion` is the version of the OpenAPI document.
- `PackageName` is the name of the package defined in `gen.yaml`.

## Feature Support

### Authentication

| Name | Support | Notes |
|------|---------|-------|
| HTTP Basic | ✅ | |
| API Key (bearer, header, cookie, query) | ✅ | |
| OAuth implicit flow | ✅ | |
| OAuth refresh token flow | ✅ using security callbacks | |
| OAuth client credentials flow | ✅ using hooks | |
| OAuth resource owner password flow | ✅ | |
| mTLS | 🏗️ Partial | |

### Server Configuration

| Name | Support | Notes |
|------|---------|-------|
| URL Templating | ✅ | defining `variables` |
| Multiple server | ✅ | `x-speakeasy-server-id` extension |
| Describe server outside your spec | ✅ | `serverUrl` config |

### Data Types

#### Basic Types

| Name | Support | Notes |
|------|---------|-------|
| Numbers | ✅ | `float`, `double`, `int32`, `int64` |
| Strings | ✅ | |
| Date Time | ✅ | |
| Boolean | ✅ | |
| Binary | ✅ | |
| Enums | ✅ | |
| Arrays | ✅ | |
| Maps | ✅ | |
| Objects | ✅ | |
| Any | ✅ | |
| Null | ✅ | |

#### Polymorphism

| Name | Support | Notes |
|------|---------|-------|
| Union Types | ✅ | `anyOf` is treated as `oneOf` and will create a union type object. |
| Intersection Types | 🏗️ Partial | |

### Methods

| Name | Support | Notes |
|------|---------|-------|
| Namespacing | ✅ | |
| Multi-level Namespacing | ✅ | |
| Custom naming | ✅ | `x-speakeasy-name-override` extension |
| Exclude Methods | ✅ | `x-speakeasy-ignore` extension |
| Deprecation | ✅ | the `deprecate` flag |

### Parameters

| Name | Support | Notes |
|------|---------|-------|
| Pass Inline | ✅ | |
| Pass via Request Object | ✅ | |
| Exclude Parameters | ✅ | `x-speakeasy-ignore` extension |
| Deprecate Parameters | ✅ | the `deprecate` flag |
| Define globally | ✅ | |

#### Path Parameters Serialization

| Name | Support | Notes |
|------|---------|-------|
| Default (style = simple, explode = false) | ✅ | |
| Basic types | ✅ | |
| Simple objects | ✅ | |
| `label` & `matrix` | ❌ | |

#### Query Parameters Serialization

| Name | Support | Notes |
|------|---------|-------|
| `json` | ✅ | |
| `form` | ✅ | |
| `spaceDelimited` | ✅ | |
| `pipeDelimited` | ✅ | |
| `deepObject` | ✅ | |
| Basic types | ✅ | |
| Simple objects | ✅ | |

### Requests

| Name | Support | Notes |
|------|---------|-------|
| Request headers | ✅ | |
| Request retries | ✅ | |
| `json` | ✅ | Both `application/json` and `text/json` |
| form data | ✅ | |
| binary | ✅ | |
| raw byte | ✅ | |
| plain text | ✅ | |
| `x-www-form-urlencoded` | 🏗️ Partial | Including encoding, but not non-object types |
| XML | ❌ | |
| Other media types | ❌ | |

### Responses

| Name | Support | Notes |
|------|---------|-------|
| Pagination | ✅ | `x-speakeasy-pagination` extension |
| Custom Errors | ✅ | `x-speakeasy-errors` extension |
| json | ✅ | |
| plain text | ✅ | |
| binary | ✅ | |
| raw byte | ✅ | |
| XML | ❌ | |
| Other media types | ❌ | |

### Documentation

| Name | Support | Notes |
|------|---------|-------|
| `README` generation | ✅ | |
| Usage Snippet generation | ✅ | |
| Documentation generation | ✅ | |

## OSS Comparison: Speakeasy vs Open Source Generators

At Speakeasy, idiomatic SDKs are created in a variety of languages, with generators that follow principles ensuring SDKs the best developer experience. The goal is to let developers focus on building great APIs and applications, without being distracted by hand-rolling custom SDKs just to get basic functionality.

Here's a summary comparing Speakeasy to popular open-source TypeScript SDK generators:

| Feature | Speakeasy | TypeScript Fetch | TypeScript Node | Oazapfts |
|---------|-----------|------------------|-----------------|----------|
| Schema validation | ✅ Using Zod | ✅ Basic | ✅ Basic | ❌ |
| Documentation generation | ✅ Full docs and examples | ❌ | ❌ | ❌ |
| OpenAPI v3.1 support | ✅ | ⚠️ Beta | ⚠️ Beta | ❌ |
| Union types/polymorphism | ✅ | ✅ | ❌ | ✅ With discriminator |
| Browser support | ✅ | ✅ | ❌ | ✅ |
| Tree-shaking support | ✅ | ⚠️ Limited | ⚠️ Limited | ⚠️ Limited |
| OAuth 2.0 | ✅ | ❌ | ❌ | ❌ |
| Retries | ✅ | ❌ | ❌ | ❌ |
| Pagination | ✅ | ❌ | ❌ | ❌ |
| React Hooks generation | ✅ With TanStack Query | ❌ | ❌ | ❌ |
| Data streaming | ✅ With runtime docs | ✅ | ✅ | ✅ |
| Node.js support | ✅ | ✅ | ✅ | ✅ |
| Deno support | ✅ | ❌ | ❌ | ❌ |
| Bun support | ✅ | ❌ | ❌ | ❌ |
| React Native support | ✅ | ❌ | ❌ | ❌ |
| Package publishing | ✅ | ❌ | ❌ | ❌ |
| CI/CD integration | ✅ GitHub Actions | ❌ | ❌ | ❌ |

### Key Differences from OpenAPI Generator

**Type Safety**: Speakeasy generates proper TypeScript union types for polymorphic objects, while OpenAPI Generator's typescript-node template flattens `oneOf` into a single class with all properties from both types, which is incorrect.

**Runtime Validation**: Speakeasy uses Zod for comprehensive runtime validation of both user input and server responses, helping detect schema drift.

**Documentation**: Speakeasy automatically generates complete documentation with working examples. OpenAPI Generator provides minimal or no documentation.

**Modern Runtime Support**: Speakeasy works across Node.js, Deno, Bun, and browsers. OpenAPI Generator templates are limited to specific environments.

**Advanced Features**: Speakeasy includes built-in support for retries, pagination, OAuth 2.0, and React Hooks. OpenAPI Generator requires manual implementation of these features.

## Dependency Management

Generated TypeScript SDKs include dependencies that require ongoing maintenance to ensure security and stability.

### Set up automated dependency scanning

We strongly recommend configuring a dependency scanning tool on your SDK repository. If your organization already uses a scanning tool, configure it for your SDK repository as well. Popular options include Dependabot (GitHub native), Snyk, and Semgrep. These tools automatically monitor your dependencies and create pull requests when updates are available.

### Keep dependencies updated

For TypeScript SDKs, lock files like `package-lock.json` freeze dependency versions at SDK generation time. To refresh to the latest secure versions:

```bash
rm -rf package-lock.json && rm -rf node_modules
npm install
```

### Adopt dependency cooldowns

Consider implementing a dependency cooldown strategy where you wait a period (for example, 7-14 days) before adopting newly-published package versions. This practice helps protect against supply chain attacks. Recent incidents have shown that compromised packages are often caught and removed within the first few days of publication. A cooldown period allows the community to vet new releases before they enter your codebase.

## Configuration Options

All TypeScript SDK configuration is managed in the `gen.yaml` file under the `typescript` section.

### Version and General Configuration

```yaml
typescript:
  version: 1.2.3
  author: "Author Name"
  packageName: "custom-sdk"
```

| Name | Required | Default Value | Description |
|------|----------|---------------|-------------|
| version | true | 0.0.1 | The current version of the SDK. |
| packageName | true | openapi | The name of the npm package. See npm package guidelines. |
| author | true | Speakeasy | The name of the author of the published package. See npm author field. |

### Additional JSON Package

```yaml
typescript:
  additionalPackageJSON:
    license: "MIT"
```

| Name | Required | Default Value | Description |
|------|----------|---------------|-------------|
| additionalPackageJSON | false | {} | Additional key/value pairs for the `package.json` file. Example: license, keywords, etc. |

### Additional Dependencies

```yaml
typescript:
  additionalDependencies:
    dependencies:
      axios: "^0.21.0"
    devDependencies:
      typescript: "^4.0.0"
    peerDependencies:
      react: "^16.0.0"
```

| Name | Required | Default Value | Description |
|------|----------|---------------|-------------|
| dependencies | false | {} | Additional production dependencies to include in the `package.json`. |
| devDependencies | false | {} | Additional development dependencies to include in the `package.json`. |
| peerDependencies | false | {} | Peer dependencies for compatibility. |

#### Common Dependency Patterns

**Crypto libraries for custom authentication:**

```yaml
# For HMAC signatures, HTTP signing, etc.
typescript:
  additionalDependencies:
    dependencies:
      crypto-js: ^4.2.0
    devDependencies:
      '@types/crypto-js': ^4.2.0
```

> **Note:** Modern Node.js (18+), Deno, and Bun support the Web Crypto API (`crypto.subtle`) natively. Use `crypto-js` only for older Node.js compatibility or specific algorithms not in Web Crypto.

**Zod extensions for structured output:**

```yaml
typescript:
  additionalDependencies:
    dependencies:
      zod-to-json-schema: ^3.24.1
```

**Logging and telemetry:**

```yaml
typescript:
  additionalDependencies:
    dependencies:
      pino: ^9.0.0
    devDependencies:
      '@types/pino': ^7.0.0
```

### Package Scripts and Examples

```yaml
typescript:
  additionalScripts:
    format: "prettier --write src"
    docs: "typedoc --out docs src"
    custom-test: "vitest run --coverage"
  generateExamples: true
  compileCommand: ["npm", "run", "build"]
```

| Name | Required | Default Value | Description |
|------|----------|---------------|-------------|
| additionalScripts | false | {} | Custom npm scripts to add to the `package.json` file. Scripts with the same name as default scripts will override them. |
| generateExamples | false | true | Whether to generate example files in an examples directory demonstrating SDK usage. |
| compileCommand | false | N/A | The command to use for compiling the SDK. Must be an array where the first element is the command and the rest are arguments. |

### Method and Parameter Management

```yaml
typescript:
  maxMethodParams: 3
  flatteningOrder: "parameters-first"
  methodArguments: "infer-optional-args"
```

| Name | Required | Default Value | Description |
|------|----------|---------------|-------------|
| maxMethodParams | false | 0 | Maximum number of parameters before an input object is created. `0` means input objects are always used. |
| flatteningOrder | false | parameters-first | Determines the ordering of method arguments when flattening parameters and body fields. Options: `parameters-first` or `body-first`. |
| methodArguments | false | infer-optional-args | Determines how arguments for SDK methods are generated. Options: `infer-optional-args` or `require-security-and-request`. |

### Security Configuration

```yaml
typescript:
  envVarPrefix: SPEAKEASY
  flattenGlobalSecurity: true
```

| Property | Description | Type | Default |
|----------|-------------|------|---------|
| flattenGlobalSecurity | Enables inline security credentials during SDK instantiation. **Recommended: `true`** | boolean | true |
| envVarPrefix | Sets a prefix for environment variables that allows users to configure global parameters and security. | string | N/A |

### Module Management

```yaml
typescript:
  moduleFormat: "dual"
  useIndexModules: true
```

| Name | Required | Default Value | Description |
|------|----------|---------------|-------------|
| useIndexModules | false | true | Controls generation of index modules (`index.ts`). Setting to `false` improves tree-shaking and build performance by avoiding barrel files. |
| moduleFormat | false | dual | Sets the module format to use when compiling the SDK. Options: `commonjs`, `esm`, or `dual`. Using `dual` provides optimal compatibility while enabling modern bundler optimizations. |

> **Note:** For optimal bundle size and tree-shaking performance in modern applications, we recommend using `moduleFormat: "dual"` together with `useIndexModules: false`. This combination ensures maximum compatibility while enabling the best possible bundler optimizations.

### Import Management

```yaml
typescript:
  imports:
    option: "openapi"
    paths:
      callbacks: models/callbacks
      errors: models/errors
      operations: models/operations
      shared: models/components
      webhooks: models/webhooks
```

| Field | Required | Default Value | Description |
|-------|----------|---------------|-------------|
| option | false | "openapi" | Defines the type of import strategy. Typically set to `"openapi"`, indicating that the structure is based on the OpenAPI document. |
| paths | false | {} | Customizes where different parts of the SDK (e.g., callbacks, errors, and operations) will be imported from. |

#### Import Paths

| Component | Default Value | Description |
|-----------|---------------|-------------|
| callbacks | models/callbacks | The directory where callback models will be imported from. |
| errors | models/errors | The directory where error models will be imported from. |
| operations | models/operations | The directory where operation models (i.e., API endpoints) will be imported from. |
| shared | models/components | The directory for shared components, such as reusable schemas, and data models imported from the OpenAPI spec. |
| webhooks | models/webhooks | The directory for webhook models, if the SDK includes support for webhooks. |

### Error and Response Handling

```yaml
typescript:
  clientServerStatusCodesAsErrors: true
  responseFormat: "flat"
  enumFormat: "union"
  defaultErrorName: "SDKError"
  baseErrorName: "HTTPError"
  acceptHeaderEnum: false
```

| Property | Description | Type | Default |
|----------|-------------|------|---------|
| responseFormat | Defines how responses are structured. Options: `envelope`, `envelope-http`, or `flat`. | string | flat |
| enumFormat | Determines how enums are generated. Options: `enum` (TypeScript enums) or `union` (union types). | string | union |
| clientServerStatusCodesAsErrors | Treats `4XX` and `5XX` status codes as errors. Set to `false` to treat them as normal responses. | boolean | true |
| defaultErrorName | The name of the fallback error class if no more specific error class is matched. Must start with a capital letter and contain only letters and numbers. | string | SDKError |
| baseErrorName | The name of the base error class used for HTTP error responses. Must start with a capital letter and contain only letters and numbers. | string | HTTPError |
| acceptHeaderEnum | Whether to generate TypeScript enums for controlling the return content type of SDK methods when multiple accept types are available. | boolean | false |

### Model Validation and Serialization

```yaml
typescript:
  jsonpath: "rfc9535"
  zodVersion: "v4-mini"
  constFieldsAlwaysOptional: false
  modelPropertyCasing: "camel"
  unionStrategy: "populated-fields"
  laxMode: "lax"
  alwaysIncludeInboundAndOutbound: false
  exportZodModelNamespace: false
```

| Property | Description | Type | Default |
|----------|-------------|------|---------|
| jsonpath | Sets the JSONPath implementation to use. Options: `legacy` (deprecated) or `rfc9535` (recommended). | string | rfc9535 |
| zodVersion | The version of Zod to use for schema validation. Options: `v3`, `v4`, or `v4-mini`. | string | v4-mini |
| constFieldsAlwaysOptional | Whether const fields should be treated as optional regardless of OpenAPI spec requirements. When `false` (recommended), const fields respect the OpenAPI spec's required array. | boolean | false |
| modelPropertyCasing | Property naming convention to use. Options: `camel` (converts to camelCase) or `snake` (converts to snake_case). | string | camel |
| unionStrategy | Strategy for deserializing union types. Options: `left-to-right` or `populated-fields` (tries all types and returns the one with the most matching fields). | string | populated-fields |
| laxMode | Controls validation strictness. When set to `lax`, required fields will be coerced to their zero value. Options: `lax` or `strict`. | string | lax |
| alwaysIncludeInboundAndOutbound | Whether to always include both inbound and outbound schemas for all types regardless of usage. | boolean | false |
| exportZodModelNamespace | Whether to export the deprecated `$` namespace containing `inboundSchema` and `outboundSchema` aliases. | boolean | false |

### Forward Compatibility

These options control how the SDK handles API evolution, allowing older SDK versions to continue working when APIs add new enum values, union types, or fields.

```yaml
typescript:
  forwardCompatibleEnumsByDefault: true
  forwardCompatibleUnionsByDefault: tagged-only
```

| Property | Description | Type | Default |
|----------|-------------|------|---------|
| forwardCompatibleEnumsByDefault | Controls whether enums used in responses are treated as open enums that accept unknown values. When `true`, SDKs gracefully handle new enum values added by the API. | boolean | true |
| forwardCompatibleUnionsByDefault | Controls whether discriminated unions accept unknown discriminator values. When set to `tagged-only`, SDKs capture unknown union variants in a type-safe way. | string | tagged-only |

> **Note:** These options work together with `laxMode` and `unionStrategy` to provide robust forward compatibility. When all four features are enabled (the default for new TypeScript SDKs), your SDK will gracefully handle API evolution including new enum values, new union types, missing fields, and type mismatches.

### Server-sent Events Configuration

```yaml
typescript:
  sseFlatResponse: false
```

| Property | Description | Type | Default |
|----------|-------------|------|---------|
| sseFlatResponse | Whether to flatten SSE (Server-Sent Events) responses by extracting the `data` field from wrapper models, providing direct access to the event data instead of the wrapper object. | boolean | false |

### Advanced Features

```yaml
typescript:
  enableReactQuery: false
```

| Property | Description | Type | Default |
|----------|-------------|------|---------|
| enableReactQuery | Generate React hooks using TanStack Query. | boolean | false |

---

## Custom Code Regions

TypeScript SDKs support custom code regions that preserve your modifications during regeneration. This feature allows you to extend generated SDK classes with custom methods while keeping the ability to regenerate.

### Enabling Custom Code Regions

```yaml
# gen.yaml
typescript:
  enableCustomCodeRegions: true
```

### Region Syntax

Use `// #region` and `// #endregion` comments to mark code that should be preserved:

```typescript
// #region imports
import { z } from "zod";
import { customHelper } from "../extra/helpers.js";
// #endregion imports

export class MyService extends ClientSDK {
    // #region sdk-class-body
    /**
     * Custom method that extends the generated SDK
     */
    async customMethod(request: CustomRequest): Promise<CustomResponse> {
        // Your custom implementation
        const transformed = customHelper(request);
        return this.generatedMethod(transformed);
    }
    // #endregion sdk-class-body

    // Generated methods appear after custom regions
    async generatedMethod(request: Request): Promise<Response> {
        // ... generated code
    }
}
```

### Region Types

| Region Name | Location | Purpose |
|-------------|----------|---------|
| `imports` | Top of file, after generated imports | Custom import statements |
| `sdk-class-body` | Inside SDK class, before generated methods | Custom methods and properties |

### How Regeneration Works

When `speakeasy run` regenerates the SDK:

1. The generator identifies `#region` / `#endregion` blocks
2. Content inside regions is preserved exactly as-is
3. Content outside regions is regenerated from the OpenAPI spec
4. Region markers themselves are preserved

### Best Practices

1. **Keep custom code minimal**: Only add what you can't achieve through OpenAPI extensions
2. **Document custom methods**: Add JSDoc comments for IDE support
3. **Use `src/extra/` for complex logic**: Import heavy implementations from extra modules
4. **Test custom code separately**: Don't rely on generated test infrastructure
5. **Version control region changes**: Track modifications in git for review

### Common Use Cases

- Adding convenience methods that wrap generated operations
- Implementing structured output parsing (e.g., with Zod)
- Adding custom serialization/deserialization logic
- Integrating with framework-specific patterns (e.g., React hooks)

> **See also:** `sdk-customization/hooks.md` for cross-cutting concerns without modifying generated files

---

## Extra Modules Pattern

For complex custom logic that doesn't fit in code regions, use a dedicated `src/extra/` directory. This pattern keeps custom code organized and testable.

### Directory Structure

```
src/
├── extra/
│   ├── README.md              # Document your extensions
│   ├── index.ts               # Export public API
│   ├── structuredOutput.ts    # Complex custom logic
│   └── helpers.ts             # Utility functions
├── hooks/
│   └── registration.ts        # Hook registrations
├── sdk/
│   └── chat.ts                # Import extras via #region
└── ...
```

### Creating Extra Modules

```typescript
// src/extra/structuredOutput.ts
import { z } from "zod";
import { zodToJsonSchema } from "zod-to-json-schema";
import { ResponseFormat } from "../models/components/responseformat.js";

/**
 * Convert a Zod schema to the API's JSON Schema format
 */
export function zodToResponseFormat<T extends z.ZodTypeAny>(
  schema: T,
  name: string = "response"
): ResponseFormat {
  const jsonSchema = zodToJsonSchema(schema);
  return {
    type: "json_schema",
    jsonSchema: {
      name,
      schemaDefinition: jsonSchema,
      strict: true,
    },
  };
}

/**
 * Parse a JSON response using a Zod schema
 */
export function parseResponse<T extends z.ZodTypeAny>(
  schema: T,
  content: string
): z.infer<T> | undefined {
  const result = schema.safeParse(JSON.parse(content));
  return result.success ? result.data : undefined;
}
```

### Integrating with Code Regions

```typescript
// src/sdk/chat.ts
// #region imports
import { z } from "zod";
import {
  zodToResponseFormat,
  parseResponse,
} from "../extra/structuredOutput.js";
// #endregion imports

export class Chat extends ClientSDK {
    // #region sdk-class-body
    /**
     * Chat completion with structured output parsing
     *
     * @remarks
     * Pass a Zod schema as responseFormat to get typed, validated responses.
     */
    async parse<T extends z.ZodTypeAny>(
        request: Omit<ChatRequest, 'responseFormat'> & { responseFormat: T },
        options?: RequestOptions
    ): Promise<ParsedChatResponse<T>> {
        // Transform Zod schema to API format
        const apiRequest = {
            ...request,
            responseFormat: zodToResponseFormat(request.responseFormat),
        };

        // Call generated method
        const response = await this.complete(apiRequest, options);

        // Parse response with Zod
        const parsed = response.choices?.[0]?.message?.content
            ? parseResponse(request.responseFormat, response.choices[0].message.content)
            : undefined;

        return {
            ...response,
            choices: response.choices?.map((choice, i) => ({
                ...choice,
                message: {
                    ...choice.message,
                    parsed: i === 0 ? parsed : undefined,
                },
            })),
        };
    }
    // #endregion sdk-class-body
}
```

### Documenting Extra Modules

Create a README in the extra directory:

```markdown
<!-- src/extra/README.md -->
# SDK Extensions

Custom logic for the SDK that extends generated functionality.

## Structured Outputs

The `structuredOutput.ts` module provides Zod integration for typed responses.

### Usage

```typescript
import { MySDK } from "@myorg/mysdk";
import { z } from "zod";

const schema = z.object({
  name: z.string(),
  age: z.number(),
});

const sdk = new MySDK({ apiKey: "..." });
const result = await sdk.chat.parse({
  model: "gpt-4",
  messages: [{ role: "user", content: "..." }],
  responseFormat: schema,
});

console.log(result.choices[0].message.parsed); // Typed!
```

## Development

To test extra modules:

```bash
npm install --prefix tests
npm run build
cd tests && npm test
```
```

### Testing Extra Modules

```typescript
// tests/extra/structuredOutput.test.ts
import { zodToResponseFormat, parseResponse } from "../../src/extra/structuredOutput";
import { z } from "zod";

describe("structuredOutput", () => {
  const schema = z.object({
    name: z.string(),
    value: z.number(),
  });

  describe("zodToResponseFormat", () => {
    it("should convert Zod schema to JSON Schema format", () => {
      const result = zodToResponseFormat(schema, "TestSchema");

      expect(result.type).toBe("json_schema");
      expect(result.jsonSchema.name).toBe("TestSchema");
      expect(result.jsonSchema.strict).toBe(true);
    });
  });

  describe("parseResponse", () => {
    it("should parse valid JSON", () => {
      const json = '{"name": "test", "value": 42}';
      const result = parseResponse(schema, json);

      expect(result).toEqual({ name: "test", value: 42 });
    });

    it("should return undefined for invalid JSON", () => {
      const json = '{"name": "test"}'; // missing value
      const result = parseResponse(schema, json);

      expect(result).toBeUndefined();
    });
  });
});
```

### Adding Runtime Dependencies

If your extra modules need additional dependencies, add them to gen.yaml:

```yaml
typescript:
  additionalDependencies:
    dependencies:
      zod: "^3.20.0"
      zod-to-json-schema: "^3.24.1"
```

---

## JSR (Deno) Publishing

TypeScript SDKs can be published to JSR (JavaScript Registry) alongside NPM, enabling native Deno support.

### What is JSR?

JSR is the JavaScript Registry for Deno and other modern runtimes. Publishing to JSR allows:

- Native Deno imports without npm specifiers
- TypeScript-first package distribution
- Automatic type inference from source

### jsr.json Configuration

Create a `jsr.json` file in your SDK root:

```json
{
  "name": "@myorg/my-sdk",
  "version": "1.0.0",
  "exports": {
    ".": "./src/index.ts",
    "./models": "./src/models/index.ts",
    "./lib/config": "./src/lib/config.ts"
  },
  "publish": {
    "include": [
      "LICENSE",
      "README.md",
      "src/**/*.ts"
    ],
    "exclude": [
      "src/**/*.test.ts",
      "src/__tests__/**"
    ]
  }
}
```

### Configuration Fields

| Field | Required | Description |
|-------|----------|-------------|
| `name` | Yes | Package name (must include scope, e.g., `@org/pkg`) |
| `version` | Yes | Semantic version |
| `exports` | Yes | Entry points mapping (must point to `.ts` files) |
| `publish.include` | No | Files to include in package |
| `publish.exclude` | No | Files to exclude from package |

### Export Mapping

Define multiple entry points for tree-shaking:

```json
{
  "exports": {
    ".": "./src/index.ts",
    "./models": "./src/models/index.ts",
    "./models/components": "./src/models/components/index.ts",
    "./models/operations": "./src/models/operations/index.ts",
    "./lib/config": "./src/lib/config.ts",
    "./lib/http": "./src/lib/http.ts",
    "./types": "./src/types/index.ts"
  }
}
```

### Publishing to JSR

```bash
# Authenticate with JSR
deno publish --token $JSR_TOKEN

# Or publish interactively
deno publish
```

### CI/CD Integration

Add JSR publishing to your GitHub Actions workflow:

```yaml
# .github/workflows/publish-jsr.yaml
name: Publish to JSR

on:
  release:
    types: [published]

jobs:
  publish:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      id-token: write  # Required for JSR provenance

    steps:
      - uses: actions/checkout@v4

      - uses: denoland/setup-deno@v2
        with:
          deno-version: v2.x

      - name: Verify version matches
        run: |
          PKG_VERSION=$(jq -r .version jsr.json)
          TAG_VERSION=${GITHUB_REF#refs/tags/v}
          if [ "$PKG_VERSION" != "$TAG_VERSION" ]; then
            echo "Version mismatch: jsr.json=$PKG_VERSION, tag=$TAG_VERSION"
            exit 1
          fi

      - name: Publish to JSR
        run: deno publish
```

### Dual Publishing (NPM + JSR)

Publish to both registries from the same workflow:

```yaml
# .github/workflows/publish.yaml
name: Publish SDK

on:
  release:
    types: [published]

jobs:
  publish-npm:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
          registry-url: 'https://registry.npmjs.org'
      - run: npm ci
      - run: npm run build
      - run: npm publish --access public
        env:
          NODE_AUTH_TOKEN: ${{ secrets.NPM_TOKEN }}

  publish-jsr:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      id-token: write
    steps:
      - uses: actions/checkout@v4
      - uses: denoland/setup-deno@v2
      - run: deno publish
```

### Using JSR Packages

Once published, users can import directly in Deno:

```typescript
// Deno - direct import from JSR
import { SDK } from "jsr:@myorg/my-sdk";

// Or with import map
// deno.json
{
  "imports": {
    "@myorg/my-sdk": "jsr:@myorg/my-sdk@^1.0.0"
  }
}
```

### Version Synchronization

Keep `package.json` and `jsr.json` versions in sync:

```bash
# Update both files together
npm version patch  # Updates package.json
jq '.version = "'"$(jq -r .version package.json)"'"' jsr.json > tmp.json && mv tmp.json jsr.json
```

Or use a script in package.json:

```json
{
  "scripts": {
    "version": "node -e \"const pkg = require('./package.json'); const jsr = require('./jsr.json'); jsr.version = pkg.version; require('fs').writeFileSync('./jsr.json', JSON.stringify(jsr, null, 2));\""
  }
}
```

---

## Pre-defined TODO List

When configuring a TypeScript SDK generation, initialize your TODO list with:

| Step | TODO Item | Active Form |
|------|-----------|-------------|
| 1 | Review TypeScript SDK feature requirements | Reviewing TypeScript SDK feature requirements |
| 2 | Configure gen.yaml for TypeScript target | Configuring gen.yaml for TypeScript target |
| 3 | Set package name and version | Setting package name and version |
| 4 | Configure module format (dual, esm, commonjs) | Configuring module format |
| 5 | Set maxMethodParams and flattening options | Setting maxMethodParams and flattening options |
| 6 | Test SDK compilation and type checking | Testing SDK compilation and type checking |

**Usage:**
```
TodoWrite([
  {content: "Review TypeScript SDK feature requirements", status: "pending", activeForm: "Reviewing TypeScript SDK feature requirements"},
  {content: "Configure gen.yaml for TypeScript target", status: "pending", activeForm: "Configuring gen.yaml for TypeScript target"},
  {content: "Set package name and version", status: "pending", activeForm: "Setting package name and version"},
  {content: "Configure module format (dual, esm, commonjs)", status: "pending", activeForm: "Configuring module format"},
  {content: "Set maxMethodParams and flattening options", status: "pending", activeForm: "Setting maxMethodParams and flattening options"},
  {content: "Test SDK compilation and type checking", status: "pending", activeForm: "Testing SDK compilation and type checking"}
])
```

**Nested workflows:**
- See `plans/sdk-generation.md` for the full SDK generation workflow
- See `spec-first/validation.md` for OpenAPI validation before generation
