### POST `/tokenize`: Tokenize a given text

*Options:*

`content`: (Required) The text to tokenize.

`add_special`: (Optional) Boolean indicating if special tokens, i.e. `BOS`, should be inserted.  Default: `false`

`parse_special`: (Optional) Boolean indicating if special tokens should be tokenized. When `false` special tokens are treated as plaintext.  Default: `true`

`with_pieces`: (Optional) Boolean indicating whether to return token pieces along with IDs.  Default: `false`

**Response:**

Returns a JSON object with a `tokens` field containing the tokenization result. The `tokens` array contains either just token IDs or objects with `id` and `piece` fields, depending on the `with_pieces` parameter. The piece field is a string if the piece is valid unicode or a list of bytes otherwise.


If `with_pieces` is `false`:
```json
{
  "tokens": [123, 456, 789]
}
```

If `with_pieces` is `true`:
```json
{
  "tokens": [
    {"id": 123, "piece": "Hello"},
    {"id": 456, "piece": " world"},
    {"id": 789, "piece": "!"}
  ]
}
```

With input 'á' (utf8 hex: C3 A1) on tinyllama/stories260k
```
{
  "tokens": [
    {"id": 198, "piece": [195]}, // hex C3
    {"id": 164, "piece": [161]} // hex A1
  ]
}
```
