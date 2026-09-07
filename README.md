# Novel Editorial Studio

面向长篇中文小说的 Codex skill。它把持续创作视为可恢复的项目流程：以 Markdown 为事实来源，围绕卷、卷段、章节、场景四层结构推进，并将规划、写作、审阅、修订、连续性和合规检查放在同一套控制体系中。

适用于百万字级连载，也适用于需要稳定续写、结构审阅或批量修订的中长篇项目。

## 能力

| 能力 | 作用 |
| --- | --- |
| 长篇规划 | 组织卷 -> 卷段 -> 章 -> 场景的层级结构，分配主线阶梯、支线节奏和字数目标。 |
| 项目控制包 | 建立并维护总控、创作决策、连续性、动态状态、伏笔、进度、情感弧线和质量债务等 Markdown 台账。 |
| 续写与修订 | 按已确认的角色动机、世界规则、视角和结局约束续写；修订时优先解决硬逻辑与因果问题。 |
| 审阅优先 | 先判断章节是否必要，再检查桥接、人物关系升温、状态变化、重复功能章与 AI 痕迹，并给出最小修正。 |
| 自动连载 | 支持按批推进的工作流：上下文装配、章节写作包、正文、机检、审计、修订、合规检查、台账回灌与检查点。 |
| 连续性管理 | 跟踪人物身份、地点、时间、资源、关系、支线和伏笔，帮助从可靠检查点恢复项目。 |
| 风格审校 | 识别模板句、提示词腔、说明书口吻、空转对话、过密总结、跨章复用与疲劳词。 |
| 平台合规 | 做内容红线与格式基线的预检，帮助将内容修订到合规范围；不提供绕过审核、伪造原创或规避 AI 披露的方案。 |
| 卷末复盘 | 汇总主线推进、支线停滞、伏笔兑现、字数进度、重复问题和用户偏好，并沉淀为下一批规则。 |

## 使用场景

- 从一个模糊创意搭建可持续创作的长篇小说工程。
- 接续已有项目，先读取现有台账和检查点再恢复写作。
- 审阅大纲、章节、场景或人物关系，定位逻辑断层与无效章节。
- 对一批章节进行结构、风格、连续性和合规的系统检查。
- 在明确边界与停机条件下，按章节或批次自动推进连载。

## Reference 功能地图

`references/` 不是一组互相独立的写作建议，而是一套按任务逐层调用的编辑控制系统。`SKILL.md` 负责判断当前处于规划、写作、审阅、修订还是自动连载模式；下面的 reference 负责提供该模式所需的具体规则、台账字段和交付标准。

| Reference | 具体功能 | 主要连接 |
| --- | --- | --- |
| [`lifecycle.md`](references/lifecycle.md) | 定义从创意简报、项目初始化、世界观与人物、双轨大纲、批次写作、审阅修复到长期连载的完整生命周期，并规定每个阶段何时可以退出。 | 总入口；连接 `templates.md`、`project-state.md`、`autonomous-pipeline.md`。 |
| [`templates.md`](references/templates.md) | 提供项目总控、决策记录、连续性台账、动态事件账本、双轨图、伏笔台账、进度台账，以及长篇索引和审计记录的字段模板。 | 所有流程的落盘格式；被 `memory-architecture.md`、`project-state.md`、`evolution.md` 共同使用。 |
| [`project-state.md`](references/project-state.md) | 规定如何从磁盘恢复项目：先读进度，再读总控、决策、连续性、动态事件、双轨图和伏笔，最后读最新正文；避免从第一章重新开始。 | 连接检查点、`book_status.py` 和上下文装配。 |
| [`scale-architecture.md`](references/scale-architecture.md) | 解决百万字项目的体量分配，将故事拆成卷、卷段、章、场景，管理主线阶梯、支线轮转、战力或资源上限、中段防塌和伏笔预算。 | 为 `story-control-model.md` 提供结构骨架，为 `autonomous-pipeline.md` 提供批次和卷级收口标准。 |
| [`memory-architecture.md`](references/memory-architecture.md) | 用 L1 常驻规则、L2 卷级战略、L3 滚动索引、L4 近期原文组织上下文；规定单章只装配相关人物、近期摘要和必要伏笔。 | 把 `project-state.md` 的恢复信息压缩成可写上下文，连接角色矩阵、资源账本和 `book_status.py`。 |
| [`story-control-model.md`](references/story-control-model.md) | 区分稳定设定、动态事件、未来计划和正文四种真相层；用承载树与因果树同时组织故事，并用场景卡和写作包把结构转换成可执行任务。 | 连接 `scale-architecture.md` 的层级结构、`memory-architecture.md` 的上下文和自动连载的写作环节。 |
| [`genre-rules.md`](references/genre-rules.md) | 为玄幻仙侠、都市、悬疑恐怖、言情提供推进机制、节奏单位、禁忌、疲劳词和启用的审计维度；项目总控可以覆盖默认规则。 | 决定 `audit-dimensions.md` 启用哪些检查，也约束 `style-and-humanity.md` 的修订方式。 |
| [`autonomous-pipeline.md`](references/autonomous-pipeline.md) | 定义人审档与自动连载档的权限边界、角色分工、单章九步主链、质量门、三轮重试、停机条件、批次交付和三类章节工件。 | 串起 `memory-architecture.md`、机检脚本、`audit-dimensions.md`、`platform-compliance.md` 和 `evolution.md`。 |
| [`audit-dimensions.md`](references/audit-dimensions.md) | 提供从硬事实、因果结构、人物、文本到合规的 32 项审计维度，并定义 block、warn、note 严重度和固定 JSON 输出格式。 | 审计员的判定框架；接收机检脚本线索，输出交给修订者和记录员。 |
| [`continuity-and-qa.md`](references/continuity-and-qa.md) | 给出审阅顺序和最小修复原则：先查时间、空间、伤病、物件和资源，再查因果、信息边界、结构、声线和标点。 | 是 `review-mode.md` 的硬逻辑基础，与 `audit-dimensions.md` 一起生成问题表。 |
| [`review-mode.md`](references/review-mode.md) | 规定审阅时先判断章节是否应该存在，再检查前后桥接、状态变化、权力跳跃、关系热度、重复功能和提示词腔，并规定问题输出顺序。 | 将审计结论转换为作者可执行的“问题、证据、最小修正”。 |
| [`style-and-humanity.md`](references/style-and-humanity.md) | 保护作者原有声线和有意的不对称，减少套话、解释性情绪、空转对白和总结式收尾；要求先修叙事架构，再修章节节奏，最后修措辞。 | 处理 `audit-dimensions.md` 的文本层问题，并防止把“去 AI 味”简化成机械替换。 |
| [`platform-compliance.md`](references/platform-compliance.md) | 区分硬红线、高风险表达和格式基线，规定真实改写路径、AI 辅助标注边界和合规检查流程；明确不提供绕审手段。 | 自动连载的合规门；与 `compliance_scan.py` 配合，但最终判定仍由人工完成。 |
| [`evolution.md`](references/evolution.md) | 每批提取新事实、重复批注、用户偏好和质量债务；重复出现的修正升级为项目规则，卷末复盘后刷新检查点。 | 把一次性审阅结果回灌到 `项目总控.md`、题材规则和下一批上下文。 |
| [`neuro-book-notes.md`](references/neuro-book-notes.md) | 说明本 skill 借鉴的四种工作流思想：Markdown 真相源、记录状态变化、分离故事顺序与因果顺序、把启发式检查当证据而非判决。 | 解释整体设计原则，不参与某一章的直接判定。 |

## Reference 之间如何协作

一次完整的章节生产通常按下面的链路运行：

```text
lifecycle
  -> templates + project-state
  -> scale-architecture + story-control-model
  -> memory-architecture
  -> autonomous-pipeline
  -> novel_audit.py / compliance_scan.py / book_status.py
  -> audit-dimensions + continuity-and-qa + review-mode
  -> style-and-humanity + platform-compliance
  -> templates 回灌
  -> evolution
```

这条链路中各模块的分工是明确的：

1. `lifecycle.md` 决定项目处在哪个阶段，`templates.md` 把阶段成果写入磁盘。
2. `project-state.md` 负责恢复停点；`scale-architecture.md` 决定长篇的结构尺度；`story-control-model.md` 把结构和因果落实为场景卡及写作包。
3. `memory-architecture.md` 从控制包中挑选本章真正需要的信息，避免把整本小说塞进上下文，也避免角色获得越界信息。
4. `autonomous-pipeline.md` 把上下文、写作、机检、审计、修订、合规、回灌和检查点串成可重复的批次流程。
5. 三个脚本只负责发现机械线索；`audit-dimensions.md`、`continuity-and-qa.md` 和 `review-mode.md` 负责人工判断问题严重度和最小修复路径。
6. `style-and-humanity.md` 处理文本表达，`platform-compliance.md` 处理发布风险；二者都不能替代上游的结构和因果修复。
7. `evolution.md` 把本批发现的问题沉淀成下一批规则，使项目越写越稳定，而不是每次重新讨论同一类错误。

## 按任务读取哪些 Reference

| 任务 | 建议读取顺序 | 得到的结果 |
| --- | --- | --- |
| 新项目或模糊创意 | `lifecycle.md` -> `templates.md` -> `genre-rules.md` | 形成项目总控、题材规则、人物与世界边界，以及第一个可恢复检查点。 |
| 继续已有项目 | `project-state.md` -> `book_status.py` -> `memory-architecture.md` | 找到最近停点、章节缺口、支线停滞和逾期伏笔，装配下一章的最小上下文。 |
| 设计长篇结构 | `scale-architecture.md` -> `story-control-model.md` -> `templates.md` | 得到卷战略、卷段目标、双轨图、章节清单和场景写作包。 |
| 审阅大纲或章节 | `continuity-and-qa.md` -> `review-mode.md` -> `style-and-humanity.md` | 按硬逻辑、桥接、状态变化、人物热度和文本问题输出证据与最小修正。 |
| 自动按批连载 | `autonomous-pipeline.md` -> `memory-architecture.md` -> `audit-dimensions.md` | 按质量门推进章节；block 必须归零，超过重试或触发停机条件就暂停并报告。 |
| 处理平台风险 | `platform-compliance.md` -> `audit-dimensions.md` | 区分真正违规、高风险表达和格式问题，改写到合规范围而不是绕过审核。 |
| 卷末或批次复盘 | `evolution.md` -> `project-state.md` -> `templates.md` | 更新规则、质量债务、卷级指标和可独立恢复的下一批入口。 |

## 内置工具

脚本只提供机械化线索，最终的剧情、风格与合规判断仍应由作者或审计员完成。

```bash
# 检查字数、章号、占位符、重复句、套话、疲劳词、段落节奏与对白比例
python3 scripts/novel_audit.py 正文/ --json

# 内容红线初筛与平台格式基线检查
python3 scripts/compliance_scan.py 正文/ --json

# 汇总项目字数、章节缺口、支线停滞与伏笔逾期情况
python3 scripts/book_status.py . --target-words 2000000 --json
```

## 安装

将本仓库放入 Codex skills 目录，并保持仓库根目录就是 skill 根目录：

```bash
git clone https://github.com/adam1943/novel-editorial-studio.git
mkdir -p "${CODEX_HOME:-$HOME/.codex}/skills"
cp -R novel-editorial-studio "${CODEX_HOME:-$HOME/.codex}/skills/"
```

重新打开或刷新 Codex 后，可使用：

```text
Use $novel-editorial-studio to review my existing novel project and identify the smallest structural fixes.
```

## 仓库结构

```text
.
├── SKILL.md                  # Codex 的主指令与行为边界
├── agents/openai.yaml        # 显示名称、默认提示与调用策略
├── references/               # 按任务按需读取的工作流与审阅参考
└── scripts/                  # 本地审计、合规预检与项目状态工具
```

## 重要边界

- Markdown 文件是项目真相源；聊天记录不应成为唯一状态存储。
- 影响结局、世界硬规则、核心人物或主视角体系的改动，需要作者先确认。
- 自动修订在同一章节内最多进行三轮；无法通过质量门时应停止并报告。
- 发布动作由作者自行完成；skill 不会代替作者向平台投稿。

## 目录说明

详细的使用方式位于 [`SKILL.md`](SKILL.md)。`references/` 下的文档按需要读取，覆盖生命周期、项目状态、自动连载、体量规划、记忆架构、审计维度、题材规则、风格、人类化表达和平台合规等主题。
