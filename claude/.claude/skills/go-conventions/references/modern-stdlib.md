# Modern stdlib idioms

Reference for the `go-conventions` skill. Reach for the modern stdlib form by default; the
pre-1.21 spelling signals that the code predates the toolchain. Each rule names the preferred
form and the one-line reason.

## Sorting

`slices.SortFunc` / `slices.SortStableFunc` with `cmp.Compare` or
`cmp.Or`, not `sort.Slice` / `sort.SliceStable`. `slices.Sort(s)`
for `[]string` / `[]int`, not `sort.Strings` / `sort.Ints`. The
comparator returns `-1/0/+1`, so multi-key sorts collapse to one
`cmp.Or(...)` line.

```go
// pre-1.21
sort.SliceStable(xs, func(i, j int) bool {
    if xs[i].Rank != xs[j].Rank { return xs[i].Rank < xs[j].Rank }
    return xs[i].Name < xs[j].Name
})

// 1.21+
slices.SortStableFunc(xs, func(a, b X) int {
    return cmp.Or(cmp.Compare(a.Rank, b.Rank), cmp.Compare(a.Name, b.Name))
})
```

## One-shot init

`sync.OnceValue[T]` / `sync.OnceFunc`, not `sync.Once` paired
with a package-level result var. The `Once` + var + wrapper trio
exists only because pre-1.21 had no return-value form.

```go
// pre-1.21
var (
    cfgOnce sync.Once
    cfg     *Config
)
func Cfg() *Config { cfgOnce.Do(func() { cfg = load() }); return cfg }

// 1.21+
var Cfg = sync.OnceValue(func() *Config { return load() })
```

## Iterators

`iter.Seq[T]` / `iter.Seq2[K,V]` for push iterators with ≥ 2
call sites. Hand-rolled `Next()/Stop()` pairs and `ForEach(func)`
callbacks are pre-1.23. Single-caller helpers can stay as plain
functions. The win is when consumers want real `break` and
loop-local state.

## Logging

`log/slog` for internal-package log calls. `fmt.Fprintln(os.Stderr,
...)` is acceptable only in `cmd/` for user-facing startup errors
that aren't log-shaped. Inside `internal/`, structured log records
beat printf strings; the receiver can filter, route, or drop them.

## Loops

`for range N` when the index is never read inside the body. The
classic three-clause `for i := 0; i < N; i++` survives only when
the body uses `i`.

```go
for range rows { ... }              // 1.22+
for i := 0; i < rows; i++ { ... }   // only if i is read
```

## Maps

`maps.Keys` / `maps.Values` (`iter.Seq` in 1.23) with
`slices.Sorted` for deterministic order, not collect-then-sort
loops. `maps.Clone` over hand-rolled copy loops.

```go
keys := slices.Sorted(maps.Keys(m))
```

## Builtins

`min` / `max` / `clear` are language builtins (1.21). Conditional
helpers (`if a < b { return a }; return b`) get inlined to the
builtin. Generic `MinInt` / `MaxInt` helpers go away.

## Comparators

`cmp.Or(a, b, c)` for nil/zero coalescing across a fixed list of
candidates, not stacked `if a != "" { return a }` chains. The
absence is a voice-lens flag, not a grep gate: a manual coalescing
chain that `cmp.Or` would collapse is what poplar's project
`simplify` skill flags in its efficiency review.

## Errors

`errors.Join(errs...)` for multi-error accumulation that all
callers see. First-error-wins still wins when call order matters
or when one error semantically supersedes the rest.

## Loop scoping (1.22)

Every `for` loop variable is per-iteration. Delete leftover
`x := x` shadow lines (workarounds for the pre-1.22
shared-variable footgun).
