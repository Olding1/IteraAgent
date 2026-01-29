# 贡献指南

感谢你对 Agent Zero 的关注！我们欢迎所有形式的贡献。

## 🤝 如何贡献

### 报告 Bug

如果你发现了 bug，请：

1. 检查 [Issues](https://github.com/yourusername/Agent_Zero/issues) 是否已有相关报告
2. 如果没有，创建新 Issue，包含：
   - 清晰的标题
   - 详细的描述
   - 复现步骤
   - 预期行为 vs 实际行为
   - 环境信息（Python 版本、操作系统等）
   - 相关日志或截图

### 提出新功能

1. 先在 [Discussions](https://github.com/yourusername/Agent_Zero/discussions) 讨论
2. 获得认可后，创建 Feature Request Issue
3. 等待维护者反馈

### 提交代码

1. **Fork 仓库**

2. **创建分支**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **开发**
   - 遵循代码规范
   - 添加测试
   - 更新文档

4. **提交**
   ```bash
   git commit -m "feat: add your feature"
   ```

   提交信息格式：
   - `feat:` 新功能
   - `fix:` Bug 修复
   - `docs:` 文档更新
   - `style:` 代码格式
   - `refactor:` 重构
   - `test:` 测试
   - `chore:` 构建/工具

5. **推送**
   ```bash
   git push origin feature/your-feature-name
   ```

6. **创建 Pull Request**
   - 清晰的标题和描述
   - 关联相关 Issue
   - 等待 Review

## 📝 代码规范

### Python 代码风格

- 遵循 [PEP 8](https://www.python.org/dev/peps/pep-0008/)
- 使用 Black 格式化代码
- 使用类型注解

```python
# 好的示例
def export_to_dify(
    graph: GraphStructure,
    agent_name: str,
    output_path: Path
) -> Path:
    """导出 Graph 到 Dify YAML 格式

    Args:
        graph: Graph 结构
        agent_name: Agent 名称
        output_path: 输出路径

    Returns:
        导出文件路径
    """
    pass
```

### 文档字符串

使用 Google 风格的文档字符串：

```python
def function_name(param1: str, param2: int) -> bool:
    """简短描述

    详细描述（可选）

    Args:
        param1: 参数1描述
        param2: 参数2描述

    Returns:
        返回值描述

    Raises:
        ValueError: 错误描述
    """
    pass
```

### 测试

- 为新功能添加测试
- 确保所有测试通过
- 测试覆盖率 > 80%

```bash
# 运行测试
pytest tests/

# 查看覆盖率
pytest --cov=src tests/
```

## 🏗️ 开发设置

### 1. 克隆仓库

```bash
git clone https://github.com/yourusername/Agent_Zero.git
cd Agent_Zero
```

### 2. 创建虚拟环境

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

### 3. 安装依赖

```bash
# 安装开发依赖
pip install -r requirements-dev.txt

# 安装项目（可编辑模式）
pip install -e .
```

### 4. 配置环境

```bash
cp .env.template .env
# 编辑 .env 文件
```

### 5. 运行测试

```bash
pytest tests/
```

## 🔍 代码审查

Pull Request 会经过以下检查：

1. **自动化测试** - 所有测试必须通过
2. **代码风格** - Black + Flake8
3. **类型检查** - mypy
4. **代码审查** - 至少一位维护者审查

## 📚 文档

### 更新文档

如果你的更改影响用户使用：

1. 更新相关文档
2. 添加示例代码
3. 更新 CHANGELOG.md

### 文档位置

- `README.md` - 项目概览
- `docs/guides/` - 使用指南
- `docs/api/` - API 文档
- `CHANGELOG.md` - 更新日志

## 🎯 优先级

我们特别欢迎以下贡献：

- 🐛 Bug 修复
- 📝 文档改进
- 🧪 测试覆盖
- 🌐 国际化
- ⚡ 性能优化

## ❓ 问题？

- 查看 [文档](docs/)
- 搜索 [Issues](https://github.com/yourusername/Agent_Zero/issues)
- 在 [Discussions](https://github.com/yourusername/Agent_Zero/discussions) 提问

## 📜 行为准则

- 尊重他人
- 建设性反馈
- 包容多样性
- 专注技术讨论

## 🙏 致谢

感谢所有贡献者！你们的贡献让 Agent Zero 变得更好。

---

**Happy Coding!** 🚀
