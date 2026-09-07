# Project State

## Resume order

1. Read `progress.md`
2. Read `项目总控.md`
3. Read `创作决策记录.md`
4. Read `连续性台账.md`
5. Read `动态状态事件账本.md`
6. Read `剧情双轨图.md`
7. Read `伏笔台账.md`
8. Read the latest manuscript files

For long serials, also read `章节摘要台账.md`, `支线进度板.md`, `角色矩阵.md`, `资源账本.md` and `质量债务.md` before drafting.

Run `scripts/book_status.py <root>` first when resuming a large project. It reports word progress, chapter gaps, subplot stalls and overdue hooks in one pass, which is faster and safer than skimming files.

## Restore the checkpoint

- Find the last completed batch.
- Identify the current stopping point.
- Rebuild any missing context from files and timestamps.
- Mark any inference explicitly instead of treating it as confirmed.

## Update rules

- Write down the current stop, next batch, open questions, and validation result after each batch.
- Never restart from chapter 1 when a checkpoint already exists.
- Keep decisions that affect the whole book in `创作决策记录.md`.
