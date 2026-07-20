# Team Workflow (3 collaborators)

Keep this simple — for a 15-day sprint you don't want git process slowing you down, but you do want to avoid overwriting each other's work.

## Branching model
- `main` — always working/demo-able. Never commit broken code directly to `main`.
- `dev` — integration branch. Everyone merges here first.
- Personal/feature branches: `<name>/<short-task>`, e.g. `riya/eligibility-checker`, `arjun/translate-layer`, `dev-name/streamlit-ui`.

## Daily flow
1. Pull latest `dev` before starting work each day:
   ```
   git checkout dev
   git pull
   ```
2. Create your branch for the day's task:
   ```
   git checkout -b yourname/day5-vector-store
   ```
3. Commit small, often — don't wait until a feature is "done" to commit:
   ```
   git add .
   git commit -m "Day 5: chromadb collection + retrieval test"
   git push -u origin yourname/day5-vector-store
   ```
4. Open a Pull Request into `dev`. Even solo hackathon teams should PR-and-merge rather than push straight to `dev` — it gives you a diff to sanity-check and a commit history judges can see.
5. At the end of each day (or each phase checkpoint in the roadmap), merge `dev` → `main` once things work end-to-end.

## Avoiding collisions
Because the roadmap is phased, the natural split is **by module, not by day** — assign each person a file/module they own for the duration of a phase:
- Person A: data collection + `load_data.py` + `build_index.py`
- Person B: `rag.py` + `translate.py`
- Person C: `eligibility_checker.py` + `src/app.py` (Streamlit)

This means you're rarely editing the same file at the same time, so merges stay clean. See `TASKS.md` for the full day-by-day split.

## Commit message convention (optional but helpful for judges skimming history)
```
Day<N>: <what changed>
```
e.g. `Day6: core RAG prompt + first end-to-end answer`

## Data changes (important)
Everyone will touch `data/schemes/*.json` during Days 1-3. To avoid merge conflicts:
- Each person works on a **separate set of scheme files** (one JSON per scheme = naturally conflict-free as long as you don't edit the same scheme file).
- Agree on who's doing which schemes in `TASKS.md` before starting Day 2.

## Protecting `main` (recommended, 2 min setup)
On GitHub: Settings → Branches → Add rule for `main` → require a pull request before merging. Prevents accidental direct pushes from wiping working code the night before demo.
