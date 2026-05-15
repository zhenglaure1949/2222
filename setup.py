"""
项目初始化脚本
Setup and initialization script
"""

import os
import sys
from pathlib import Path


def create_directory_structure():
    """创建项目目录结构"""
    print("📁 创建项目目录结构...")
    
    directories = [
        "agent",
        "modules",
        "knowledge_base/guidelines",
        "knowledge_base/cases",
        "knowledge_base/resources",
        "utils",
        "tests",
        "data/cache"
    ]
    
    for directory in directories:
        path = Path(directory)
        path.mkdir(parents=True, exist_ok=True)
        print(f"  ✓ 创建目录: {directory}")


def create_init_files():
    """创建__init__.py文件"""
    print("\n📝 创建包初始化文件...")
    
    packages = [
        "agent",
        "modules",
        "utils",
        "tests"
    ]
    
    for package in packages:
        init_file = Path(package) / "__init__.py"
        if not init_file.exists():
            init_file.touch()
            print(f"  ✓ 创建: {init_file}")


def create_env_file():
    """创建.env文件"""
    print("\n⚙️  配置环境变量...")
    
    if not Path(".env").exists():
        print("  ℹ️  .env 文件不存在，请复制 .env.example 到 .env 并填入API密钥")
        print("  $ cp .env.example .env")


def check_python_version():
    """检查Python版本"""
    print("\n🐍 检查Python版本...")
    
    required_version = (3, 9)
    current_version = sys.version_info[:2]
    
    if current_version >= required_version:
        print(f"  ✓ Python版本满足要求: {sys.version.split()[0]}")
        return True
    else:
        print(f"  ✗ Python版本过低: {sys.version.split()[0]}")
        print(f"    需要: Python {required_version[0]}.{required_version[1]}+")
        return False


def print_next_steps():
    """打印后续步骤"""
    print("\n" + "="*60)
    print("✅ 项目初始化完成！")
    print("="*60)
    print("""
📋 后续步骤:

1. 配置环境变量:
   cp .env.example .env
   编辑 .env 文件，填入你的 API 密钥

2. 安装依赖:
   pip install -r requirements.txt

3. 运行示例:
   python examples.py

4. 运行测试:
   pytest tests/ -v

5. 启动Agent:
   python main.py

📚 更多信息:
   - 查看 README.md
   - 访问 GitHub: https://github.com/zhenglaure1949/2222

═══════════════════════════════════════════════════════════════
    """)


def main():
    """主初始化函数"""
    print("\n" + "█"*60)
    print("█  肾内科医学文献Agent系统 - 项目初始化")
    print("█  Medical Literature Agent - Project Initialization")
    print("█"*60)
    
    # 检查Python版本
    if not check_python_version():
        sys.exit(1)
    
    # 创建目录结构
    create_directory_structure()
    
    # 创建初始化文件
    create_init_files()
    
    # 检查.env文件
    create_env_file()
    
    # 打印后续步骤
    print_next_steps()


if __name__ == "__main__":
    main()
