"""
医学文献Agent - 使用示例
Medical Literature Agent - Usage Examples
"""

from agent import MedicalLiteratureAgent


def example_1_search_literature():
    """示例1: 搜索文献"""
    print("\n" + "="*70)
    print("示例 1: 搜索文献")
    print("="*70)
    
    agent = MedicalLiteratureAgent()
    
    # 在PubMed中搜索慢性肾脏病
    result = agent.search_literature(
        query="chronic kidney disease",
        source="pubmed",
        limit=10
    )
    
    print("\n搜索结果:")
    print(f"  源: {result.get('source')}")
    print(f"  查询: {result.get('query')}")
    print(f"  总数: {result.get('total')}")


def example_2_get_guideline():
    """示例2: 查询医学指南"""
    print("\n" + "="*70)
    print("示例 2: 查询医学指南")
    print("="*70)
    
    agent = MedicalLiteratureAgent()
    
    # 查询KDIGO CKD指南
    result = agent.get_guideline(
        guideline="kdigo",
        topic="CKD"
    )
    
    print("\n指南信息:")
    print(f"  指南: {result.get('name')}")
    print(f"  URL: {result.get('url')}")
    print(f"  主题: {result.get('topics')}")


def example_3_translate_text():
    """示例3: 翻译文献"""
    print("\n" + "="*70)
    print("示例 3: 翻译文献")
    print("="*70)
    
    agent = MedicalLiteratureAgent()
    
    # 翻译英文文本
    text = "Chronic kidney disease is characterized by progressive loss of kidney function."
    result = agent.translate_text(
        text=text,
        target_lang="zh-CN"
    )
    
    print("\n翻译结果:")
    print(f"  原文: {result.get('original')}")
    print(f"  目标语言: {result.get('target_lang')}")
    print(f"  翻译: {result.get('translated')}")


def example_4_extract_data():
    """示例4: 提取数据"""
    print("\n" + "="*70)
    print("示例 4: 提取数据")
    print("="*70)
    
    agent = MedicalLiteratureAgent()
    
    # 从论文中提取摘要
    result = agent.extract_data(
        paper_id="PMID:12345678",
        extraction_type="abstract"
    )
    
    print("\n提取结果:")
    print(f"  论文ID: {result.get('paper_id')}")
    print(f"  提取类型: {result.get('extraction_type')}")
    print(f"  消息: {result.get('message')}")


def example_5_query_database():
    """示例5: 查询公共数据库"""
    print("\n" + "="*70)
    print("示例 5: 查询公共数据库")
    print("="*70)
    
    agent = MedicalLiteratureAgent()
    
    # 在GEO数据库中查询肾脏相关数据
    result = agent.query_database(
        database="geo",
        query="kidney disease gene expression",
        limit=10
    )
    
    print("\n查询结果:")
    print(f"  数据库: {result.get('database')}")
    print(f"  数据库名称: {result.get('database_name')}")
    print(f"  查询: {result.get('query')}")
    print(f"  总数: {result.get('total')}")


def example_6_comprehensive_search():
    """示例6: 综合搜索"""
    print("\n" + "="*70)
    print("示例 6: 综合搜索")
    print("="*70)
    
    agent = MedicalLiteratureAgent()
    
    # 进行综合搜索
    result = agent.comprehensive_search(query="肾脏疾病诊疗")
    
    print("\n综合搜索结果:")
    print(f"  查询: {result.get('query')}")
    print(f"  时间: {result.get('timestamp')}")
    print(f"  搜索来源:")
    for source in result.get('results', {}).keys():
        print(f"    - {source}")


def example_7_search_history():
    """示例7: 查看搜索历史"""
    print("\n" + "="*70)
    print("示例 7: 查看搜索历史")
    print("="*70)
    
    agent = MedicalLiteratureAgent()
    
    # 执行几个搜索
    agent.search_literature("chronic kidney disease")
    agent.get_guideline("kdigo")
    agent.translate_text("Nephrotic syndrome")
    
    # 获取搜索历史
    history = agent.get_search_history()
    
    print(f"\n总搜索数: {len(history)}")
    print("\n搜索历史:")
    for i, record in enumerate(history, 1):
        print(f"\n  [{i}] {record['timestamp']}")
        print(f"      动作: {record['action']}")
        print(f"      参数: {record['params']}")


def example_8_system_info():
    """示例8: 系统信息"""
    print("\n" + "="*70)
    print("示例 8: 系统信息")
    print("="*70)
    
    agent = MedicalLiteratureAgent()
    agent.print_info()


def run_all_examples():
    """运行所有示例"""
    print("\n" + "█"*70)
    print("█" + " "*68 + "█")
    print("█" + "  医学文献Agent - 使用示例演示".center(68) + "█")
    print("█" + "  Medical Literature Agent - Examples".center(68) + "█")
    print("█" + " "*68 + "█")
    print("█"*70)
    
    try:
        example_1_search_literature()
        example_2_get_guideline()
        example_3_translate_text()
        example_4_extract_data()
        example_5_query_database()
        example_6_comprehensive_search()
        example_7_search_history()
        example_8_system_info()
        
        print("\n" + "█"*70)
        print("✅ 所有示例执行完成！")
        print("█"*70)
    
    except Exception as e:
        print(f"\n❌ 执行出错: {e}")


if __name__ == "__main__":
    run_all_examples()
