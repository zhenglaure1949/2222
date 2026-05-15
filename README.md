# 肾内科医学文献智能Agent系统

## 项目概述

这是一个专为肾内科医生设计的AI Agent系统，用于快速、高效地查阅和管理国内外医学文献、指南、临床病例和实验数据库资源。

## 核心功能模块

### 1. 文献检索模块 (Literature Search)
- **PubMed/MEDLINE**: 国际医学文献数据库
- **中国知网 (CNKI)**: 国内学术文献
- **维普 (VIP)**: 中文期刊数据库
- **万方数据**: 中文医学文献
- **医学文献国际检索**: 多语言支持

### 2. 医学指南库 (Guidelines Database)
- **肾脏病学指南**
  - KDIGO (Kidney Disease: Improving Global Outcomes)
  - 美国肾脏学会 (ASN) 指南
  - 中国医学科学院肾脏病指南
  - 欧洲肾脏病学会 (ERA-EDTA) 指南
  
- **专科指南分类**
  - 慢性肾脏病 (CKD)
  - 急性肾损伤 (AKI)
  - 肾小球肾炎
  - 肾脏置换治疗
  - 电解质与酸碱平衡

### 3. 中医药资源 (TCM Resources)
- 中医经典著作数据库
- 中医肾脏病诊疗方案
- 中西医结合临床研究文献
- 中药复方配伍数据库

### 4. 临床病例库 (Clinical Cases)
- 典型病例汇报
- PPT演示资源
- 病例讨论记录
- 诊疗经验总结

### 5. 公共数据库 (Public Databases)
- **GEO (Gene Expression Omnibus)**: 基因表达数据
- **TCGA**: 肿瘤基因图谱
- **ClinicalTrials.gov**: 临床试验注册
- **BioRxiv/MedRxiv**: 预印本服务器
- **Figshare**: 研究数据共享

### 6. 工具集成 (Tools Integration)
- 文献翻译助手
- 文献管理工具 (Zotero/Mendeley 集成)
- 数据提取与分析
- 论文速读 (Abstract 快速解析)

## 技术架构

```
┌─────────────────────────────────────────────┐
│      肾内科医学文献智能Agent系统             │
├─────────────────────────────────────────────┤
│                                              │
│  ┌──────────────────────────────────────┐   │
│  │   用户界面 (CLI / Web Dashboard)      │   │
│  └──────────────────┬───────────────────┘   │
│                     │                        │
│  ┌──────────────────▼───────────────────┐   │
│  │   Agent 核心引擎 (LLM + RAG)         │   │
│  └──────────────────┬───────────────────┘   │
│                     │                        │
│  ┌──────────────────▼───────────────────┐   │
│  │   工具链 (Tools Orchestration)       │   │
│  │  ├─ 文献搜索工具                     │   │
│  │  ├─ 指南检索工具                     │   │
│  │  ├─ 翻译工具                        │   │
│  │  ├─ 数据提取工具                     │   │
│  │  └─ 数据分析工具                     │   │
│  └──────────────────┬───────────────────┘   │
│                     │                        │
│  ┌──────────────────▼───────────────────┐   │
│  │   数据源整合 (Data Integration)      │   │
│  │  ├─ PubMed API                      │   │
│  │  ├─ 中文数据库 API                   │   │
│  │  ├─ 公共数据库链接                   │   │
│  │  └─ 本地知识库                      │   │
│  └──────────────────────────────────────┘   │
│                                              │
└─────────────────────────────────────────────┘
```

## 快速开始

### 环境需求
- Python 3.9+
- pip 或 conda

### 安装

```bash
# 克隆仓库
git clone https://github.com/zhenglaure1949/2222.git
cd 2222

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt
```

### 配置

1. 创建 `.env` 文件并配置API密钥：
```
OPENAI_API_KEY=your_key_here
PUBMED_API_KEY=your_key_here
BAIDU_TRANSLATE_API=your_key_here
```

2. 初始化本地知识库

### 使用示例

```python
from agent import MedicalLiteratureAgent

# 初始化Agent
agent = MedicalLiteratureAgent()

# 查询示例
# 1. 搜索文献
result = agent.search_literature("慢性肾脏病 诊疗指南", source="pubmed")

# 2. 查询指南
guidelines = agent.get_guidelines("KDIGO CKD")

# 3. 提取数据
data = agent.extract_data("COVID-19 对肾脏的影响")

# 4. 翻译论文
translation = agent.translate_paper(paper_id)
```

## 目录结构

```
2222/
├── README.md                    # 项目说明
├── requirements.txt             # 依赖管理
├── .env.example                 # 环境变量示例
│
├── agent/                       # Agent核心模块
│   ├── __init__.py
│   ├── main_agent.py            # 主Agent类
│   ├── tools.py                 # 工具集合
│   └── config.py                # 配置管理
│
├── modules/                     # 功能模块
│   ├── literature_search.py     # 文献搜索
│   ├── guidelines.py            # 指南管理
│   ├── chinese_medicine.py      # 中医资源
│   ├── clinical_cases.py        # 临床病例
│   ├── databases.py             # 公共数据库
│   └── translation.py           # 翻译工具
│
├── knowledge_base/              # 本地知识库
│   ├── guidelines/              # 指南文档
│   ├── cases/                   # 病例库
│   └── resources/               # 资源链接
│
├── utils/                       # 工具函数
│   ├── api_client.py            # API客户端
│   ├── text_processing.py       # 文本处理
│   └── cache.py                 # 缓存管理
│
└── tests/                       # 测试用例
    └── test_agent.py
```

## 关键资源链接

### 国际权威数据库
- [PubMed](https://pubmed.ncbi.nlm.nih.gov/)
- [KDIGO 指南](https://kdigo.org/)
- [UpToDate](https://www.uptodate.com/)

### 国内数据库
- [中国知网 (CNKI)](https://www.cnki.net/)
- [医学文献查询系统](http://www.chinankish.com/)
- [丁香园 (DXY)](https://www.dxy.cn/)

### 公共数据库
- [GEO Database](https://www.ncbi.nlm.nih.gov/geo/)
- [ClinicalTrials.gov](https://clinicaltrials.gov/)
- [BioRxiv](https://www.biorxiv.org/)

## 功能开发路线图

- [ ] Phase 1: 基础文献搜索功能
- [ ] Phase 2: 多语言指南库整合
- [ ] Phase 3: 中医药资源模块
- [ ] Phase 4: 临床病例库建设
- [ ] Phase 5: Web Dashboard 开发
- [ ] Phase 6: 离线模式支持

## 常见用途

1. **快速文献综述**: "给我总结最近3年慢性肾脏病治疗指南的主要更新"
2. **诊疗参考**: "这个患者符合哪个KDIGO指南分类，推荐的治疗方案是什么？"
3. **病例学习**: "帮我找5个经典的肾小球肾炎病例PPT"
4. **数据查询**: "在GEO数据库中找肾脏疾病相关的基因表达数据"
5. **文献翻译**: "翻译这篇最新的新英格兰医学杂志文章"

## 贡献指南

欢迎提交改进建议和新的功能模块！

## 许可证

MIT License

## 联系方式

如有问题或建议，请提交 Issue 或 Pull Request

---

**更新日期**: 2026-05-15
**维护者**: 肾内科医学文献Agent项目
