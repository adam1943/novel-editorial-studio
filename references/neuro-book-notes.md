# NeuroBook Notes

## Borrowed pattern

- Markdown Studio: treat Markdown files as the truth source.
- World Engine: store changes and state transitions, not only the latest summary.
- Plot Workbench: separate story order from causal order.
- llmlint: use style checks as review signals, not automatic truth.

## Adaptation for this skill

- Keep all novel control data in local Markdown files.
- Preserve explicit checkpoints so a project can resume after interruption.
- Promote repeated corrections into standing rules.
- Treat heuristics as evidence for review, not as final judgment.

## Other referenced projects

`inkos`: five-role relay pipeline (radar, architect, writer, auditor, reviser), seven truth files, per-genre rule packs, per-book rule overrides, multi-dimension audit, and quality gating with bounded retries. Adopted as `autonomous-pipeline.md`, `audit-dimensions.md` and `genre-rules.md`.

`AI-Novel-Writing-Assistant`: one-line idea to full-book direction, staged checkpoints with takeover and retry, per-chapter context assembled from only the participating characters, and a writing-style engine kept as a reusable asset. Adopted as the context assembly rule in `memory-architecture.md` and the stop conditions in `autonomous-pipeline.md`.

`WriteHERE`: recursive task decomposition with heterogeneous task types and dynamic adaptation rather than a fixed outline. Adopted as the volume/segment/chapter/scene decomposition in `scale-architecture.md`, where only the current and next volume are detailed.

`sepia`: AI traces live in narrative architecture before wording, so revision order runs structure first, then chapter progression, then diction. It also warns that applying every de-AI rule creates its own fingerprint. Adopted in `style-and-humanity.md` and the audit ordering.
