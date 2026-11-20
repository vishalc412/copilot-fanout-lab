# Delta update: the code changed since the bible was written

Use when a finished or nearly finished analysis exists and the code under it has moved on: a pull, a branch switch, a merge, a copied folder. Update the pages that the change touches; do not start the analysis again.

When the repository has a `.git` folder, `tracking-codebase-changes` does the same with the branch's history: it finds the commit an older analysis was written from without a list from the person, says which commit changed which function, and keeps `CHANGELOG.md`. It uses `delta.py`'s functions, so everything below about markers, stamps and the loop holds there too. This page is the way without history: a folder copied without `.git`, or a history that cannot be read.

## The person's part

The skill never runs source control. A person brings the working tree to the code the bible should describe (`git pull`, `git switch feature/x`, ...) and tells you its name for the record ("feature/x after today's pull"). That name is the `--label`; never look it up.

`scripts/delta.py` compares the files on disk with the fingerprint recorded the last time the analysis matched the code (`ledger/baseline.json`). It needs no network and no history: only the two trees, one recorded and one on disk.

## Which start

| On disk | Start |
| --- | --- |
| `ledger/baseline.json` exists | Step 1 |
| No baseline; the code has **not** changed since the analysis | `delta.py --init --label <name>`, then stop: later changes start at step 1 |
| No baseline; the code **has** changed since the analysis | Ask the person for the list of files changed since the commit the analysis was written from, saved to a file. `git diff --name-status <that commit>` is one way, run by them; a plain list of paths also works. Then `delta.py --init --changed <file> --label <name>` and go to step 3 |
| No baseline, nobody can say what changed | Treat every source file as changed: re-run the loop on the whole analysis (`next.py`), which finds what is missing but not what is stale. Tell the user that cards on unchanged-looking files are not re-checked |

## Steps

1. **Report.** `python3 -I <this skill>/scripts/delta.py --repo . --analysis <folder> --label <name>`. Read `ledger/delta.md`: files changed, added, removed and renamed, functions changed, added, removed and only moved, routes added and removed, and how many citations would move or be marked. Show the user the counts in one line. Done when `delta.md` is written.
2. **Apply.** The same command with `--apply`. It changes only pages in the output folder:
   - a citation inside a stamped card follows the card's code: the stamp finds the function wherever it is now, so the card's citations move with it, whichever branch wrote the card;
   - any other citation is moved from the version of its file the page records (the `<!-- cites path@version -->` lines at the end of each page), when every cited line survived;
   - a renamed file's path is rewritten in citations, `Source file:` lines and front matter;
   - every citation that cannot be placed that way gets `<!-- recheck: was <old citation> -->` right after it: a moved line number is never a guess;
   - each page's records are set to the files as they are now;
   - the work left (cards to rewrite or write, cards, endpoints and pages to remove) is recorded in `ledger/baseline.json`, and the baseline now matches the code on disk;
   - one row is added to `delta-log.md`.
   Done when it prints `next: ... next.py`. Running it again with no new change does nothing.
3. **The loop.** Run `next.py` as in the Workflow. While delta work is open it prints `NEXT DELTA` jobs before any packet: one file at a time (rewrite each changed card from the code, write each added one, delete what the code no longer has), then each page still carrying a recheck marker, then the knowledge base. Each card job names the stamp to put on the card's Source line (`<!-- code: 3f9a1c2b7d4e -->`); a card is done when it carries the stamp of the code as it is now. A marker is done when you have opened the code, corrected the citation and the sentence it supports, and deleted the marker. After the delta jobs the loop carries on as usual: new files get packets, and the gate runs.
4. **The pages around the change.** For each file the jobs touched, update the component README, the endpoint index, the data dictionary, the call graphs and the HLD pages where they describe what changed. `scripts/impact.py` of `assessing-change-impact` lists the pages that rest on a symbol when the graph exists.
5. **Finish.** `next.py` prints `DONE` when the gate passes, which needs no stale stamp and no recheck marker left. Set the front page status to `UPDATED FOR CODE CHANGES (<label>, <date>; <n> cards rewritten, not re-verified)`. Tell the user the changed parts are unverified, and that `verifying-a-codebase-analysis` can check them: `delta-log.md` and `ledger/delta.md` name every file and function the update touched.

If the code changes again before you finish (another pull), `next.py` prints `NEXT DELTA: the code changed`; run step 2 again. Open work carries over: it follows renames, and a card whose function has since been removed becomes a removal.

## What counts as a change

Each line is fingerprinted after `normalize_line` in `scripts/inventory.py` (trailing spaces dropped). A function is **changed** when any of its lines fingerprints differently, **moved** when every line is the same and only the position changed. A removed file and an added file with the same extension and at least half their lines in common are one file, renamed and edited. Configuration files whose name suggests secrets (`.env*`, keys, certificates, names with `secret`, `token`, `password`, `credential`) keep a whole-file fingerprint only, so every citation into them is marked when they change.

The baseline holds fingerprints, never code. It lives in `ledger/`; leave `ledger/` out when the bible is shared outside the team that has the code.

## The records at the end of each page

`delta.py --init`, `--apply` and `next.py` write one line per cited file at the end of every page: `<!-- cites app/service.py@<40 hex> -->`, the version of that file the page's line numbers count in (the Git blob id, computed from the content; no Git command). They do not render. Never write or edit them by hand: `next.py` adds them to pages written during the loop, `--apply` updates them. A page whose record is not the file on disk is placed by `--apply`; `next.py` says so before anything else.

## Working as a team

Several people may update the analysis on their own branches. The folder carries a `.gitattributes` (written by `--init` and `--apply`) that tells Git how to merge it:

| Files | Merge |
| --- | --- |
| Pages (`*.md`) | Whole file. A page changed on both sides is never mixed line by line, since its line numbers would count against two versions of the code: Git keeps your side and reports a conflict |
| `CHANGELOG.md`, `delta-log.md` | Both sides kept |
| Generated files in `ledger/` and `knowledge/` | Your side kept; the scripts rebuild them |

The rule for the person who merges: **on any conflict inside the analysis folder, keep the file as Git left it (your side), mark it resolved, finish the merge, then run the update** (`tracking-codebase-changes`, or step 1 here). Nothing is lost by keeping one side: the other side's code is in the merged tree, so its changed functions come back as work (stale stamps, marked citations, cards for code that no longer exists), and their pages are redone by the loop.

Someone who changes code and does not update the analysis leaves no damage either: the next update, by anyone, finds those changes. Commit the analysis folder only after `next.py` prints `DONE`, so every page carries its records.

Older folders without `.gitattributes` get mixed merges. `--apply` then drops conflict blocks that hold only record lines (their citations are rechecked), uses your side of a conflicted `ledger/baseline.json`, and leaves any page with another conflict untouched and names it: resolve it by keeping one whole side.

## Branches

The bible describes one tree at a time. To follow two branches, keep one output folder per branch (`codebase-analysis-main/`, `codebase-analysis-feature-x/`), each with its own baseline, and pass the matching `--analysis`. Switching one folder back and forth between branches works, but every switch is a delta that rewrites cards.
