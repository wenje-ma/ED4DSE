# ED4DSE

<div align="center">

<a href="https://github.com/wenje-ma/ED4DSE">
  <img src="https://img.shields.io/badge/ED4DSE-00C896?style=for-the-badge&logo=bookstack&logoColor=white" alt="ED4DSE"/>
  <img src="https://img.shields.io/badge/%E7%8A%B6%E6%80%81-%E5%B7%B2%E5%AE%8C%E7%BB%93-00A878?style=for-the-badge&logo=verified&logoColor=white" alt="已完结"/>
  <img src="https://img.shields.io/badge/V._Roshan_Joseph-00875F?style=for-the-badge&logo=readthedocs&logoColor=white" alt="V. Roshan Joseph"/>
</a>

**Experimental Design for Data Science and Engineering** · 全书学习笔记与代码 · ✅ 2026-09-05 完结

</div>

《Experimental Design for Data Science and Engineering》是 **V. Roshan Joseph**（佐治亚理工学院）撰写的试验设计教科书（Chapman & Hall/CRC, Texts in Statistical Science, 2026 第一版，开放获取）。这本书回答一个核心问题：**如何用最少的实验与计算，从数据中提取最多的信息**——从高斯过程建模、空间填充设计，到序贯设计与贝叶斯优化、模型校准与大数据子采样。

本仓库是对这本书的**完整学习记录**：11 章逐章笔记、逐章可运行代码、书中方法对应的 R 包，以及一条把「原书 PDF → 笔记 → Markdown → LaTeX」串起来的学习流水线。

## 📁 仓库结构

| 目录 | 内容 |
|---|---|
| `笔记/` | 11 章记忆索引型读书笔记（Ch01–Ch11.md），附笔记生成指令 |
| `markdown/` | 55 个逐小节笔记（Chxx-xx.md）、`figures/` 配图、全书 PDF（246 页） |
| `代码/` | 逐章可运行代码 Ch01–Ch11.ipynb 与数据（`data/`：RData 图数据、CSV 数据集） |
| `R包/` | 书中方法对应 R 包：`mined`（最小能量设计）、`support`（支撑点） |
| `tex/` | LaTeX 排版版笔记（document.tex → document.pdf） |
| `*.py` | 学习流水线脚本（见下） |

## 📖 章节总览

| # | 章节 | 核心内容 |
|---|---|---|
| 1 | 实验 | 响应曲面；仿真实验与物理实验；预测 / 优化 / 校准三种用途 |
| 2 | 建模技术 | 插值：多项式、RBF、克里金、高斯过程；回归：线性、核岭、高斯过程回归 |
| 3 | 基于模型的设计 | 预测型设计；最大熵设计 |
| 4 | 空间填充设计 | 聚类设计、Minimax / Maximin、拉丁超立方、MaxPro（约束区域 / 定性因子 / 分支 / 嵌套）、最小能量设计（贝叶斯计算 / 候选集 / 连续保真度参数） |
| 5 | 代表点 | 均匀设计与均匀性；非均匀分布：变换法、支撑点、不确定性传播、Population QMC |
| 6 | 筛选设计 | 方差基 / 导数基敏感性分析；Morris 筛选；MOFAT |
| 7 | 序贯设计 | 仿真代理：预测基 / 熵基序贯设计；贝叶斯优化；逆设计 |
| 8 | 部分因子设计 | 两水平设计；贝叶斯启发设计；多水平设计 |
| 9 | 模型校准 | 非线性最优设计（解析模型 / 昂贵模型 + GP 代理）；稳健设计 |
| 10 | 数据子采样 | 支撑点子采样；数据划分；数据孪生；有监督压缩 |
| 11 | 数据分析 | 因子选择与排序；孪生高斯过程 |

## 🛠 学习流水线

仓库根目录的脚本记录了整本书的学习工作流：

- `pdf_to_txt.py` —— 原书 PDF → 文本
- `ipynb_run_figs.py` —— 运行 notebook 并输出配图
- `ipynb_to_md.py` —— notebook → Markdown
- `md_merge.py` —— 合并章节 Markdown
- `md_to_tex.py` —— Markdown → LaTeX

## ▶️ 复现与使用

- 笔记：`笔记/`（整章版）与 `markdown/`（逐小节版）互为补充
- 代码：`代码/Ch01–Ch11.ipynb`，依赖 R + Python（Jupyter），数据与中间结果在 `代码/data/`
- R 包：`R包/mined`（Minimum Energy Designs，Joseph et al. 2019）与 `R包/support`（Support Points，Mak & Joseph 2018），均来自 CRAN

## 📚 原书信息

- 书名：**Experimental Design for Data Science and Engineering**
- 作者：V. Roshan Joseph（Georgia Institute of Technology）
- 出版：Chapman & Hall/CRC · Texts in Statistical Science 系列 · 2026 第一版
- 获取：开放获取（Taylor & Francis eBooks Open Access）

> 笔记为个人学习整理，公式与结论以原书为准；如有疏漏欢迎指出。
