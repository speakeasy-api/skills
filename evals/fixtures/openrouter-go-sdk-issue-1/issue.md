# GitHub Issue #1: Initial feedback

**Repository:** OpenRouterTeam/go-sdk
**Author:** adamdecaf
**Created:** 2026-01-28
**URL:** https://github.com/OpenRouterTeam/go-sdk/issues/1

---

I was excited to see a Go SDK for open router. I know it's generated with Speakeasy (we use them at [Moov](http://github.com/moovfinancial), but I wanted to give some initial feedback after using the Chat APIs.

<details>
<summary>"Tell me a story about a frog by a small lake."</summary>

```go
package openrouter_test

import (
	"context"
	"fmt"
	"os"
	"strings"
	"testing"

	openrouter "github.com/OpenRouterTeam/go-sdk"
	"github.com/OpenRouterTeam/go-sdk/models/components"
	"github.com/stretchr/testify/require"
)

func TestExample(t *testing.T) {
	apiKey := strings.TrimSpace(os.Getenv("OPENROUTER_API_KEY"))
	if apiKey == "" || testing.Short() {
		t.Skip("")
	}

	ctx := context.Background()

	client := openrouter.New(openrouter.WithSecurity(apiKey))

	req := components.ChatGenerationParams{
		Messages: []components.Message{
			{
				SystemMessage: &components.SystemMessage{
					Content: components.SystemMessageContent{
						Str: openrouter.String("You are a helpful assistant who only speaks in a 1700's british tone."),
					},
				},
			},
			{
				UserMessage: &components.UserMessage{
					Content: components.UserMessageContent{
						Str: openrouter.String("Tell me a story about a frog by a small lake."),
					},
				},
			},
		},
		Model: openrouter.String("deepseek/deepseek-v3.2"),
	}

	resp, err := client.Chat.Send(ctx, req)
	require.NoError(t, err)

	if resp.ChatResponse != nil {
		fmt.Printf("response:\n")
		fmt.Printf("  ID: %v\n", resp.ChatResponse.ID)
		fmt.Printf("  Created: %.2f\n", resp.ChatResponse.Created)
		fmt.Printf("  Model: %v\n", resp.ChatResponse.Model)

		usage := resp.ChatResponse.Usage
		fmt.Printf("  Tokens: Prompt=%.2f  Completion=%.2f  Total=%.2f\n",
			usage.PromptTokens, usage.CompletionTokens, usage.TotalTokens)

		for _, choice := range resp.ChatResponse.Choices {
			var finish string
			if f := choice.GetFinishReason(); f != nil {
				finish = string(*f)
			}

			fmt.Printf("response number %.2f - %s\n", choice.Index, finish)
			// ... rest of output handling ...
		}
	}
}
```

</details>

<details>
<summary>Output</summary>

```
response:
  ID: gen-1769633428-pepMvpFzeyAl16kl0pmo
  Created: 1769633428.00
  Model: deepseek/deepseek-v3.2
  Tokens: Prompt=31.00  Completion=645.00  Total=676.00
response number 0.00 - stop
Message:
*(Clears throat with a delicate handkerchief)* Pray, allow me to recount...
```

</details>

## Feedback Points

- **Some values being floats are weird.** Can `ChatResponseChoice.Index` really be a float? Isn't that just an int?

- **`ChatResponse.Created` could be a `time.Time` type in Go** - that's easier to work with.

- **Token usage counts**, are they a float because int64 is too small?

- **There seem to be extra pointers**, e.g. `FinishReason` - can it be nil or would `error` be used?
