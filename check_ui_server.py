#!/usr/bin/env python3
"""
诊断脚本：检查 UI 服务器配置
"""
import os
import sys

def check_files():
    """检查必要文件是否存在"""
    print("=" * 50)
    print("检查文件...")
    print("=" * 50)
    
    files_to_check = [
        'ui_server.py',
        'web/index.html',
        'web/app.js',
        'config/supervisord.app.conf'
    ]
    
    all_ok = True
    for file_path in files_to_check:
        exists = os.path.exists(file_path)
        status = "✓" if exists else "✗"
        print(f"{status} {file_path}")
        if not exists:
            all_ok = False
    
    return all_ok

def check_imports():
    """检查必要的导入"""
    print("\n" + "=" * 50)
    print("检查依赖...")
    print("=" * 50)
    
    try:
        import flask
        print(f"✓ Flask {flask.__version__}")
    except ImportError as e:
        print(f"✗ Flask 未安装: {e}")
        return False
    
    try:
        import pandas
        print(f"✓ pandas {pandas.__version__}")
    except ImportError as e:
        print(f"✗ pandas 未安装: {e}")
        return False
    
    try:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from src.service.review_service import ReviewService
        print("✓ ReviewService 可以导入")
    except ImportError as e:
        print(f"✗ ReviewService 导入失败: {e}")
        return False
    
    return True

def check_ui_server():
    """尝试启动 UI 服务器（仅检查配置）"""
    print("\n" + "=" * 50)
    print("检查 UI 服务器配置...")
    print("=" * 50)
    
    try:
        # 检查文件内容
        with open('ui_server.py', 'r', encoding='utf-8') as f:
            content = f.read()
            
        if 'Flask' in content and 'ui_app' in content:
            print("✓ ui_server.py 包含 Flask 应用")
        else:
            print("✗ ui_server.py 格式不正确")
            return False
            
        if 'send_from_directory' in content:
            print("✓ 包含静态文件服务")
        else:
            print("✗ 缺少静态文件服务")
            return False
            
        if 'port = int(os.environ.get(\'UI_PORT\', 5002))' in content:
            print("✓ 端口配置正确 (5002)")
        else:
            print("⚠ 端口配置可能不正确")
            
    except Exception as e:
        print(f"✗ 检查失败: {e}")
        return False
    
    return True

def check_supervisord():
    """检查 supervisord 配置"""
    print("\n" + "=" * 50)
    print("检查 supervisord 配置...")
    print("=" * 50)
    
    try:
        with open('config/supervisord.app.conf', 'r', encoding='utf-8') as f:
            content = f.read()
            
        if '[program:ui_server]' in content:
            print("✓ 包含 ui_server 配置")
        else:
            print("✗ 缺少 ui_server 配置")
            return False
            
        if 'python /app/ui_server.py' in content or 'python ui_server.py' in content:
            print("✓ ui_server 启动命令正确")
        else:
            print("⚠ ui_server 启动命令可能不正确")
            
    except Exception as e:
        print(f"✗ 检查失败: {e}")
        return False
    
    return True

def main():
    print("\n" + "=" * 50)
    print("UI 服务器诊断工具")
    print("=" * 50 + "\n")
    
    results = []
    results.append(("文件检查", check_files()))
    results.append(("依赖检查", check_imports()))
    results.append(("UI 服务器配置", check_ui_server()))
    results.append(("supervisord 配置", check_supervisord()))
    
    print("\n" + "=" * 50)
    print("诊断结果")
    print("=" * 50)
    
    all_ok = True
    for name, result in results:
        status = "✓ 通过" if result else "✗ 失败"
        print(f"{name}: {status}")
        if not result:
            all_ok = False
    
    print("\n" + "=" * 50)
    if all_ok:
        print("✓ 所有检查通过！")
        print("\n如果仍然无法访问，请检查：")
        print("1. 服务是否正在运行: docker-compose ps 或 ps aux | grep ui_server")
        print("2. 端口是否被占用: lsof -i :5002 或 netstat -tuln | grep 5002")
        print("3. 防火墙设置: 确保 5002 端口开放")
        print("4. 查看日志: docker-compose logs ui_server 或查看 supervisord 日志")
    else:
        print("✗ 发现问题，请根据上述检查结果修复")
    print("=" * 50 + "\n")

if __name__ == '__main__':
    main()

