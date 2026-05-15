"""
交互式CLI主程序
Interactive Command Line Interface
"""

import sys
from agent import MedicalLiteratureAgent


def print_welcome():
    """打印欢迎信息"""
    print("\n" + "█"*70)
    print("█" + " "*68 + "█")
    print("█" + "  🏥 肾内科医学文献智能Agent系统".center(68) + "█")
    print("█" + "  Medical Literature AI Agent for Nephrology".center(68) + "█")
    print("█" + " "*68 + "█")
    print("█"*70)
    print()


def print_menu():
    """打印菜单"""
    print("\n" + "="*70)
    print("📋 功能菜单 (Main Menu)")
    print("="*70)
    print("""
    1. 📚 搜索文献 (Search Literature)
    2. 📖 查询指南 (Query Guidelines)
    3. 🌐 翻译文献 (Translate Text)
    4. 📊 提取数据 (Extract Data)
    5. 🔍 查询数据库 (Query Database)
    6. 🎯 综合搜索 (Comprehensive Search)
    7. 📋 查看搜索历史 (View Search History)
    8. ℹ️  系统信息 (System Info)
    9. ❌ 退出 (Exit)
    """)
    print("="*70)


def menu_search_literature(agent):
    """搜索文献"""
    print("\n📚 搜索文献")
    query = input("  输入搜索关键词 (Enter search query): ").strip()
    if not query:
        print("  ✗ 关键词不能为空")
        return
    
    source = input("  选择数据库 (pubmed/cnki) [default: pubmed]: ").strip() or "pubmed"
    limit = input("  输入返回结果数量 [default: 10]: ").strip()
    limit = int(limit) if limit.isdigit() else 10
    
    print(f"\n  🔄 正在搜索 {source}...")
    result = agent.search_literature(query, source=source, limit=limit)
    
    print("\n  📍 搜索结果:")
    for key, value in result.items():
        print(f"    {key}: {value}")


def menu_get_guideline(agent):
    """查询指南"""
    print("\n📖 查询医学指南")
    print("  可用指南: kdigo, asn, era-edta, china")
    guideline = input("  选择指南 [default: kdigo]: ").strip() or "kdigo"
    topic = input("  输入主题 (可选): ").strip()
    
    print(f"\n  🔄 正在查询 {guideline}...")
    result = agent.get_guideline(guideline=guideline, topic=topic)
    
    print("\n  📍 指南信息:")
    for key, value in result.items():
        print(f"    {key}: {value}")


def menu_translate_text(agent):
    """翻译文献"""
    print("\n🌐 翻译文献")
    text = input("  输入待翻译文本: ").strip()
    if not text:
        print("  ✗ 文本不能为空")
        return
    
    target_lang = input("  选择目标语言 (zh-CN/en-US) [default: zh-CN]: ").strip() or "zh-CN"
    
    print(f"\n  🔄 正在翻译...")
    result = agent.translate_text(text=text, target_lang=target_lang)
    
    print("\n  📍 翻译结果:")
    for key, value in result.items():
        print(f"    {key}: {value}")


def menu_extract_data(agent):
    """提取数据"""
    print("\n📊 提取数据")
    paper_id = input("  输入论文ID: ").strip()
    if not paper_id:
        print("  ✗ 论文ID不能为空")
        return
    
    extraction_type = input("  输入提取类型 (abstract/tables/findings) [default: abstract]: ").strip() or "abstract"
    
    print(f"\n  🔄 正在提取数据...")
    result = agent.extract_data(paper_id=paper_id, extraction_type=extraction_type)
    
    print("\n  📍 提取结果:")
    for key, value in result.items():
        print(f"    {key}: {value}")


def menu_query_database(agent):
    """查询数据库"""
    print("\n🔍 查询公共数据库")
    print("  可用数据库: geo, tcga, clinicaltrials, biorxiv, medrxiv")
    database = input("  选择数据库: ").strip()
    if not database:
        print("  ✗ 数据库不能为空")
        return
    
    query = input("  输入搜索查询: ").strip()
    if not query:
        print("  ✗ 查询不能为空")
        return
    
    limit = input("  输入返回结果数量 [default: 10]: ").strip()
    limit = int(limit) if limit.isdigit() else 10
    
    print(f"\n  🔄 正在查询 {database}...")
    result = agent.query_database(database=database, query=query, limit=limit)
    
    print("\n  📍 查询结果:")
    for key, value in result.items():
        print(f"    {key}: {value}")


def menu_comprehensive_search(agent):
    """综合搜索"""
    print("\n🎯 ��合搜索")
    query = input("  输入搜索关键词: ").strip()
    if not query:
        print("  ✗ 关键词不能为空")
        return
    
    print(f"\n  🔄 正在进行综合搜索...")
    result = agent.comprehensive_search(query)
    
    print("\n  📍 综合搜索结果:")
    print(f"    查询: {result['query']}")
    print(f"    时间: {result['timestamp']}")
    print("\n    搜索来源:")
    for source in result['results'].keys():
        print(f"      - {source}")


def menu_search_history(agent):
    """查看搜索历史"""
    print("\n📋 搜索历史")
    history = agent.get_search_history()
    
    if not history:
        print("  (无搜索历史)")
        return
    
    for i, record in enumerate(history, 1):
        print(f"\n  [{i}] {record['timestamp']}")
        print(f"      动作: {record['action']}")
        print(f"      参数: {record['params']}")


def menu_system_info(agent):
    """系统信息"""
    print("\n")
    agent.print_info()


def main():
    """主程序"""
    print_welcome()
    
    # 初始化Agent
    try:
        agent = MedicalLiteratureAgent()
        print("✅ Agent已成功初始化\n")
    except Exception as e:
        print(f"❌ 初始化失败: {e}")
        sys.exit(1)
    
    # 主菜单循环
    while True:
        print_menu()
        choice = input("请选择功能 (Select function) [1-9]: ").strip()
        
        try:
            if choice == "1":
                menu_search_literature(agent)
            elif choice == "2":
                menu_get_guideline(agent)
            elif choice == "3":
                menu_translate_text(agent)
            elif choice == "4":
                menu_extract_data(agent)
            elif choice == "5":
                menu_query_database(agent)
            elif choice == "6":
                menu_comprehensive_search(agent)
            elif choice == "7":
                menu_search_history(agent)
            elif choice == "8":
                menu_system_info(agent)
            elif choice == "9":
                print("\n👋 谢谢使用 (Thank you for using)!")
                break
            else:
                print("\n❌ 无效选择 (Invalid choice)")
        
        except KeyboardInterrupt:
            print("\n\n⚠️  程序已中断 (Program interrupted)")
            break
        except Exception as e:
            print(f"\n❌ 错误: {e}")


if __name__ == "__main__":
    main()
