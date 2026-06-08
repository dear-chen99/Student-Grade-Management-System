


# 学生成绩管理系统

一个基于 Python Tkinter 构建的现代化学生成绩管理系统，提供成绩录入、编辑、统计分析、数据导入导出等完整功能。

## 功能特性

- **用户登录**: 安全的学生账号登录验证系统
- **成绩管理**: 支持添加、修改、删除学生成绩记录
- **科目设置**: 灵活配置考试科目
- **班级管理**: 按班级统计和分析成绩数据
- **数据分析**: 提供多维度统计分析图表（柱状图、折线图、雷达图、箱线图等）
- **数据导入导出**: 支持 CSV/Excel 格式的数据导入导出
- **预警提示**: 自动识别成绩异常和待关注学生
- **实时搜索**: 快速检索学生信息和成绩数据

## 技术栈

- Python 3.x
- Tkinter (GUI 图形界面)
- JSON (数据存储)
- Matplotlib (数据可视化)

## 环境配置

```bash
pip install -r requirements.txt
```

## 运行程序

```bash
python main.py
```

或直接运行登录入口：

```bash
python modules/login.py
```

## 数据文件

系统默认使用 `data/grades.json` 文件存储所有学生成绩数据。首次运行时会自动创建数据文件。

## 主要模块说明

| 模块 | 说明 |
|------|------|
| DM | 数据管理器，负责数据的增删改查、统计分析等核心业务逻辑 |
| App | 主应用程序，构建完整的图形用户界面 |
| GradientFrame | 渐变色背景画布组件 |
| ModernCard | 现代风格卡片组件 |
| LoginWindow | 登录窗口模块 |

## 系统截图

<div align="center">
  <img src="resources/Login.png" width="400" alt="登录界面">
  <br>
  <img src="resources/Home Page.png" width="600" alt="主页界面">
</div>

## License

MIT License