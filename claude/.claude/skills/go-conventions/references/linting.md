# Linting

Reference for the `go-conventions` skill.

`.golangci.yml`:

```yaml
version: "2"

linters:
  default: none
  enable:
    - errcheck
    - govet
    - ineffassign
    - staticcheck
    - unused
    - modernize
    - misspell
    - unparam
  settings:
    errcheck:
      check-type-assertions: true

formatters:
  enable:
    - gofmt
    - goimports
```

The `version: "2"` key is required. A v1-schema file fails against a
v2 binary with "unsupported version of the configuration", which is
easy to mistake for a missing linter when a Makefile swallows the
error.

`default: none` plus an explicit enable list is the legible form,
and it is also load-bearing: v2's `default: none` drops errcheck,
unused, and ineffassign unless you name them. `staticcheck` in v2
subsumes the old `gosimple` and `stylecheck`. `modernize` (built in
since v2.6.0) reports stale stdlib idioms, so a separate grep pass
for them is redundant. Verify a config with
`golangci-lint config verify` before committing it.

No `nolint` pragmas. Fix the code instead. Where a project must
allow them, enable `nolintlint` and require both a rule id and a
reason, so every suppression is legible to a reviewer.
