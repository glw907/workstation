#!/usr/bin/env bash
set -uo pipefail

# check-moves.sh: the draft check for the repo-organization deletions. It reads the migration map
# and, for every row that moved something out of this repo, confirms three facts:
#   1. the destination path exists on the destination repo's default branch (through `gh`);
#   2. for a plain docs move, each destination file equals the source file at the row's pin, or
#      differs only where a `~/.dotfiles/<old path>` or `~/Projects/<repo>/<new path>` reference was rewritten.
#      A collision row keeps the destination, and a code row is rewritten on arrival, so
#      neither compares content; and
#   3. the source path is unchanged between the pin and the head ref, so nothing edited the file
#      after it was copied.
# A failure on any row exits 1 and names the row. A stays, deferred, or flagged row is not checked.
#
# Usage: check-moves.sh --map MAP [--repo DIR] [--head REF] [--dest-root DIR]
#   --repo       the source repo (default: the current directory)
#   --head       the ref the source must still match (default: origin/main)
#   --dest-root  read destinations from DIR/<repo>/<path> instead of GitHub (tests)

map=""
repo="."
head="origin/main"
dest_root=""
while [[ $# -gt 0 ]]; do
    case "$1" in
        --map)       map="${2:?--map needs a path}"; shift 2 ;;
        --repo)      repo="${2:?--repo needs a directory}"; shift 2 ;;
        --head)      head="${2:?--head needs a ref}"; shift 2 ;;
        --dest-root) dest_root="${2:?--dest-root needs a directory}"; shift 2 ;;
        *) echo "check-moves: unknown argument $1" >&2; exit 2 ;;
    esac
done
[[ -n "$map" && -f "$map" ]] || { echo "check-moves: --map is required" >&2; exit 2; }

tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT

fail=0
checked=0
rewritten=0
# Counted apart from the loop below, so a row the loop skips by mistake shows as a short count.
expected=$(awk -F'\t' 'NR > 1 && $6 != "stays" && $6 !~ /^deferred:/ && $6 != "flagged"' "$map" | wc -l)

# The reference forms a destination session rewrites: the old home path of every row and the new
# home path of every row, one per line. A moved file may differ from its source only where these
# appear, and the longest go first so a file path is stripped whole before its folder.
awk -F'\t' 'NR > 1 && $2 != "" {
    old = $2; sub(/\/$/, "", old); print "~/.dotfiles/" old
    if ($4 != "") { new = $4; sub(/\/$/, "", new); print "~/Projects/" $3 "/" new }
}' "$map" | awk '{ print length($0) "\t" $0 }' | sort -rn | cut -f2- > "$tmp/ref-forms"

# dest_exists <repo> <path>: succeeds when the destination path is present.
dest_exists() {
    if [[ -n "$dest_root" ]]; then
        [[ -e "$dest_root/$1/$2" ]]
    else
        gh api "repos/glw907/$1/contents/${2%/}" > /dev/null 2>&1
    fi
}

# dest_fetch <repo> <path> <out>: writes the destination file's bytes to <out>.
dest_fetch() {
    if [[ -n "$dest_root" ]]; then
        cp "$dest_root/$1/$2" "$3"
    else
        gh api -H 'Accept: application/vnd.github.raw' "repos/glw907/$1/contents/$2" > "$3"
    fi
}

# strip_refs <in> <out>: deletes every rewritable reference form from <in>, byte for byte, so two
# files that differ only in those references come out identical.
strip_refs() {
    perl -e 'open(F, "<", shift) or die; chomp(my @f = <F>); local $/; my $t = <STDIN>;
        for my $f (@f) { $t =~ s/\Q$f\E\/?//g } print $t' "$tmp/ref-forms" < "$1" > "$2"
}

# content_matches <old> <new_repo> <new_path> <pin>: compares one source file with its destination.
content_matches() {
    local src_file="$1" dst_repo="$2" dst_file="$3" pin="$4"
    git -C "$repo" show "$pin:$src_file" > "$tmp/src" 2> /dev/null || return 1
    dest_fetch "$dst_repo" "$dst_file" "$tmp/dst" 2> /dev/null || return 1
    cmp -s "$tmp/src" "$tmp/dst" && return 0
    strip_refs "$tmp/src" "$tmp/src.stripped"
    strip_refs "$tmp/dst" "$tmp/dst.stripped"
    if cmp -s "$tmp/src.stripped" "$tmp/dst.stripped"; then
        rewritten=$((rewritten + 1))
        return 0
    fi
    return 1
}

while IFS=$'\037' read -r _ old_path new_repo new_path _ state pin; do
    case "$state" in
        ''|stays|deferred:*|flagged|state) continue ;;
    esac
    checked=$((checked + 1))
    row="$old_path ($state)"

    if [[ "$state" != leaves-with-pings ]]; then
        if ! dest_exists "$new_repo" "$new_path"; then
            echo "FAIL missing destination: $row -> $new_repo:$new_path"
            fail=1
            continue
        fi
    fi

    if [[ "$state" == moved && "$old_path" == docs/superpowers/* ]]; then
        base="${old_path%/}"
        row_ok=1
        while IFS= read -r f; do
            [[ -n "$f" ]] || continue
            rel="${f#"$base"}"
            if ! content_matches "$f" "$new_repo" "${new_path%/}$rel" "$pin"; then
                echo "FAIL destination differs from the source at the pin: $row ($f)"
                row_ok=0
            fi
        done < <(git -C "$repo" ls-tree -r --name-only "$pin" -- "$base")
        [[ "$row_ok" -eq 1 ]] || { fail=1; continue; }
    fi

    if ! git -C "$repo" diff --quiet "$pin" "$head" -- "$old_path"; then
        echo "FAIL source edited after the pin: $row"
        fail=1
    fi
done < <(tr '\t' '\037' < "$map"; echo)

echo "check-moves: checked $checked of $expected moved rows ($rewritten files differ only in rewritten references)"
if [[ "$checked" -ne "$expected" ]]; then
    echo "FAIL checked-row count does not match the map"
    fail=1
fi
[[ "$fail" -eq 0 ]] && echo "check-moves: ok"
exit "$fail"
