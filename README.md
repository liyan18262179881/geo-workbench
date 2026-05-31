# GEO 工作台 · 本地生活版

针对本地生活领域的 **GEO（生成式引擎优化）** B端客户管理系统。帮助本地门店在豆包等 AI 搜索引擎中提升品牌可见性。

## 核心功能

四步标准流程，逐步推进：

1. **客户诊断** — 填写公司信息，自动判断场景、EEAT缺口、行业敏感度
2. **关键词部署** — 按本地B2C公式自动生成关键词，三阶段优先级排列
3. **豆包市场检测** — 逐词查询豆包，记录竞品占位情况，生成市场判断报告
4. **文章生产** — 一键调用 AI 生成符合 GEO 规范的平台文章，直接复制发布

## 支持的 AI 平台

- 🔵 DeepSeek
- 🫧 豆包（字节跳动）
- 🌙 Kimi（Moonshot）
- 🟠 通义千问（Qwen）
- 🟤 Claude（Anthropic）
- 🟢 OpenAI（GPT）

## 快速启动

```bash
# 安装依赖
pip3 install anthropic openai

# 启动本地服务
python3 server.py
```

浏览器打开 **http://localhost:8765**

## 方法论来源

基于 GEO 自动化 Skill 整合包，所有流程严格遵守：
- `doubao-geo-publisher` 主流程规范
- `geo-keyword-miner` 关键词挖掘规则
- `geo-article-writer` 文章生成规范
- `geo-doubao-research` 豆包检测流程

## License

MIT
