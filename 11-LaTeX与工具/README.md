# 11 LaTeX 模板与论文工具

> 2026-07-12 直接核验（WebFetch/WebSearch 实测链接可用）。模板选定后应在 2026 年 12 月对照当年官方格式要求（25 页、Summary Sheet 首页、AI Report 不计页）再确认一次。

## 0. 本目录已内置模板

`mcmthesis/` 是 [latexstudio-org/mcmthesis](https://github.com/latexstudio-org/mcmthesis) 的完整拷贝（LPPL v1.3c 许可证允许再分发，LICENSE 已保留）：
- `mcmthesis.pdf` / `mcmthesis-demo.pdf` —— 使用文档和效果示例，先看这两个
- `mcmthesis.dtx` —— 文档类源文件
- `code/` —— 示例工程，可直接复制出来当队伍模板起点

## 1. 美赛专用 LaTeX 模板（推荐顺序）

| 模板 | 链接 | 说明 |
|---|---|---|
| **mcmthesis**（社区标准） | https://github.com/Liam0205/mcmthesis （原版）；https://github.com/latexstudio-org/mcmthesis （维护分支，release 6.3.2） | 专为 MCM/ICM 设计的 LaTeX 文档类，自动生成带控制号的 Summary Sheet 首页；已收录 CTAN：https://ctan.org/pkg/mcmthesis |
| Overleaf 在线模板 | https://www.overleaf.com/latex/templates/latex-template-for-mcm-icm/rwgdhsxfxkwj | 标注适配 2024 格式；**推荐用 Overleaf 做三人实时协作** |
| icmmcm（Harvey Mudd） | https://github.com/harveymuddcollege/icmmcm | 美方院校维护的替代类，风格更朴素 |
| 论文+资料合集 | https://github.com/yicheng-dev/Material-of-MCM-ICM | LaTeX 模板 + 历年优秀论文 + MATLAB 书 |

使用建议：
- 主用 **mcmthesis（latexstudio-org 分支）+ Overleaf**：开箱即得 Summary Sheet、目录、定理环境；
- 9 月就把模板跑通并按 O 奖论文结构改造成"队伍骨架模板"（章节预置：Assumptions / Data Cleaning / EDA / 分问 / Sensitivity / Strengths & Weaknesses / Memo / References / Report on Use of AI Tools）；
- 检查模板的 AI Report 章节是否在页码计数之外（旧模板可能没有此章节，需手动加在 `\end{document}` 前并核对页数逻辑）。

## 2. 图表风格（评委 10 分钟初审的生死线）

- 统一用 matplotlib + seaborn，赛前定死全队样式表（配色、字号、图例位置），存成 `.mplstyle` 文件；
- 每图必有：坐标轴标签（含单位）、图例、**结论性 caption**（"图 X 显示…"而不是"结果图"）；
- 模型总览图/技术路线图：draw.io 或亿图图示，O 奖论文标配；
- 参考对象：O 奖论文的图（见 10 的下载渠道），模仿其信息密度与风格统一度。

## 3. 协作与版本管理

- 论文：Overleaf（免费版够用，付费版可 track changes）；
- 代码与数据：GitHub 私有仓库（赛中内容**绝不能公开**，比赛期间公开等于违规泄题）；
- AI 交互台账：共享表格（工具/版本/日期/Query/Output），格式见 10。
