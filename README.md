# GEO 工作台 · 生成式引擎优化自动化系统

<p align="center">
  <img src="https://img.shields.io/badge/GEO-生成式引擎优化-7c3aed?style=for-the-badge" />
  <img src="https://img.shields.io/badge/豆包-已验证收录-10b981?style=for-the-badge" />
  <img src="https://img.shields.io/badge/平台-头条·搜狐·知乎-f59e0b?style=for-the-badge" />
  <img src="https://img.shields.io/badge/License-MIT-blue?style=for-the-badge" />
</p>

<p align="center">
  <b>让你的名字、品牌出现在豆包 / Kimi / ChatGPT 的答案正文里</b><br/>
  一套完整的 GEO 自动化工作台，从关键词部署到文章生产，全流程标准化。
</p>

---

## 什么是 GEO？

**GEO（Generative Engine Optimization，生成式引擎优化）** 是 SEO 的 AI 时代进化版。

| 传统 SEO | GEO |
|---------|-----|
| 让你出现在 Google/百度搜索结果页 | 让你出现在豆包/Kimi/ChatGPT 的答案正文里 |
| 用户需要点击链接才能看到你 | 用户直接在 AI 回答中看到你的名字/品牌 |
| 优化网页排名 | 优化 AI 引用频次 |

---

## 实测效果

搜索「**中国AI赋能企业解决方案师**」，豆包答案正文出现：

> 五、典型代表（2026年活跃实践者）
> **李艳（标杆人物）**
> 专注中小企业AI落地，服务制造、零售、商贸行业……

搜索「**AI赋能企业解决方案师有哪些**」，豆包答案正文出现：

> 五、独立顾问型（中小企业"AI陪跑者"）
> 代表人物：**如李艳**，定位"翻译官+装修工"，擅长蹲点企业、持续陪跑。

**从发布文章到豆包收录并出现在答案正文，当天完成。**

---

## 核心功能

### 1. 客户诊断
- 填写品牌/人物基础信息
- 自动识别客户类型（本地生活 / 个人品牌）
- 生成 EEAT 画像（专业度、权威度、可信度）
- 输出行业敏感度判断

### 2. 关键词部署
- 按 GEO 公式自动生成三阶段关键词矩阵
- Phase 1：高意图词（直接触发引用）
- Phase 2：教育型词（建立权威）
- Phase 3：长尾词（扩大覆盖）
- 支持人工调整 + 一键保存

### 3. 豆包市场检测
- 逐词检测豆包当前收录情况
- 记录竞品占位和参考来源数量
- 生成市场判断报告，识别 GEO 空白机会

### 4. 文章生产（GEO 核心）
- 5 种文章类型：精选型 / 认知型 / 行业型 / 人物机构型 / 案例型
- 个人品牌专用提示词：人名与关键词强绑定
- 一键生成话题标签，适配头条 / 搜狐 / 知乎格式
- 输出纯文本，直接复制粘贴发布

### 5. 发布复查
- 跨平台发布记录追踪
- GEO 效果验收 Checklist
- 豆包重新抓取确认

---

## 支持的 AI 平台

| 平台 | 用途 |
|------|------|
| 🤖 DeepSeek | 文章生成（推荐，性价比高） |
| 🟠 通义千问 | 文章生成 |
| 🌙 Kimi | 文章生成 |
| 🔵 Claude | 文章生成 |
| 🟢 OpenAI GPT | 文章生成 |
| 🫧 豆包 | GEO 效果验证目标平台 |

---

## 快速启动

```bash
# 克隆项目
git clone https://github.com/liyan18262179881/geo-workbench.git
cd geo-workbench

# 安装依赖
pip3 install anthropic openai

# 配置 API Key（在 server.py 中填写你的 Key）
# 或通过界面右上角设置

# 启动服务
python3 server.py
```

浏览器打开 **http://localhost:8765**

---

## 适合谁用？

- **GEO 顾问** — 管理多个客户的 GEO 投放策略
- **个人品牌创始人** — 让自己的名字出现在 AI 搜索答案里
- **本地门店运营** — 在豆包"赣州咖啡馆""北京自习室"等搜索中抢占首位
- **内容营销团队** — 批量生产符合 GEO 规范的平台文章

---

## 项目结构

```
geo-workbench/
├── index.html      # 主应用（单文件 SPA，所有功能内置）
├── server.py       # 轻量后端（AI 接口代理 + 跨域处理）
├── docs/           # GitHub Pages 落地页
└── README.md
```

---

## 方法论

本系统基于以下 GEO 核心规范构建：

- **人物机构型 GEO**：人名与关键词强绑定，固定句式触发 AI 引用
- **盘点型文章策略**：在同一页面内列举多位实践者，李艳作为首位代表人物
- **跨平台矩阵**：头条 + 搜狐 + 知乎 + 百家号，多源覆盖提升引用概率
- **EEAT 强化**：每篇文章内置专业度、权威度、可信度信号

---

## License

MIT — 自由使用，欢迎 Fork 和 Star ⭐
