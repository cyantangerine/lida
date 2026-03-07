#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
SQLite 数据库初始化脚本
用于创建所有必要的数据库表
"""

from lida.ext.entity import Base, engine, Chat, Goal, Edit, Explain, Evaluate, User


def init_database():
    """初始化数据库，创建所有表"""
    print("正在初始化 SQLite 数据库...")
    
    # 创建所有表
    Base.metadata.create_all(bind=engine)
    
    print("✓ 数据库表创建成功！")
    print("\n已创建的表:")
    print("  - t_chat (聊天表)")
    print("  - t_goal (目标表)")
    print("  - t_edit (编辑表)")
    print("  - t_explain (解释表)")
    print("  - t_evaluate (评估表)")
    print("  - users (用户表)")
    print("\n数据库文件位置：lida.db")


if __name__ == "__main__":
    init_database()
