# OpenRouter Go SDK Issue #1 Test Fixture

This fixture contains a snapshot of the OpenRouter Go SDK OpenAPI spec and GitHub issue for testing type improvement overlays.

## Source

- **Repository:** https://github.com/OpenRouterTeam/go-sdk
- **Commit:** `c2c3c701312ed9c362b305af03718de51c03758d` (2026-01-26)
- **Issue:** https://github.com/OpenRouterTeam/go-sdk/issues/1

## Test Purpose

Evaluate whether the agent can:
1. Read a GitHub issue describing type ergonomics problems
2. Identify the correct schema paths in the OpenAPI spec
3. Create an overlay that fixes the types appropriately
4. Respect constraints (NOT modify finish_reason nullability)

## Expected Fixes

| Schema Path | Current | Expected Fix |
|-------------|---------|--------------|
| `ChatResponseChoice.properties.index` | `type: number` | `type: integer` |
| `ChatResponse.properties.created` | `type: number` | Add `format: date-time` |
| `ChatGenerationTokenUsage.properties.completion_tokens` | `type: number` | `type: integer` |
| `ChatGenerationTokenUsage.properties.prompt_tokens` | `type: number` | `type: integer` |
| `ChatGenerationTokenUsage.properties.total_tokens` | `type: number` | `type: integer` |

## Should NOT be Modified

- `__schema6` (finish_reason nullability) - This is nullable because streaming responses don't have a finish_reason until complete
- `ChatCompletionFinishReason` - The enum values are correct

## Bonus Fixes (nested details)

- `completion_tokens_details.reasoning_tokens`
- `prompt_tokens_details.cached_tokens`
- `ChatStreamingResponseChunk.data.created`

## API Validation

If `OPENROUTER_API_KEY` is set, the test can make a real API call to verify that the proposed type changes match the actual API response types.
