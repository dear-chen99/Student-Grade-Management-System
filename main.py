# -*- coding: utf-8 -*-

from app import App
from modules.login import LoginWindow

if __name__ == "__main__":
    try:
        # 1. 启动登录窗口
        login = LoginWindow()
        # 2. 如果 `run()` 返回 True，则启动主程序
        if login.run():
            App().run()
        else:
            print("登录已取消")
    except Exception as e:
        # 如果登录模块有误，直接进入主程序（容错）
        print(f"登录模块加载失败 ({e})，直接进入主程序")
        App().run()