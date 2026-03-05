# Pre-Publish Checklist

完成以下检查后即可发布到 PyPI 和 npm。

## ✅ 准备工作（已完成）

- [x] 更新 setup.py 包名为 `openclaw-quant-analyst`
- [x] 创建 pyproject.toml
- [x] 创建 MANIFEST.in
- [x] 创建 package.json（npm）
- [x] 创建 Node.js CLI wrapper
- [x] 添加 MIT LICENSE
- [x] 创建发布脚本
- [x] 提交到 GitHub

## 📋 发布前检查

### 1. 测试 Python 包

```bash
# 构建包
cd /home/justin/openclaw-quant-analyst
python3 -m pip install --upgrade build
python3 -m build

# 检查包内容
tar -tzf dist/openclaw-quant-analyst-0.1.0.tar.gz | head -20

# 本地安装测试
pip install dist/openclaw-quant-analyst-0.1.0-py3-none-any.whl

# 测试导入
python3 -c "from openclaw_quant import Strategy, Backtest; print('✓ Import works')"

# 测试 CLI
openclaw-quant-analyst --help
```

### 2. 测试 npm 包

```bash
# 检查包内容
cd /home/justin/openclaw-quant-analyst
npm pack --dry-run

# 本地测试
npm link
openclaw-quant-analyst help
```

## 🚀 发布步骤

### 选项 A：自动发布（推荐）

```bash
cd /home/justin/openclaw-quant-analyst
./scripts/publish-all.sh
```

### 选项 B：分步发布

#### 发布到 PyPI

```bash
# 1. 获取 PyPI API token
# 访问: https://pypi.org/manage/account/token/

# 2. 配置 ~/.pypirc
cat > ~/.pypirc <<EOF
[pypi]
username = __token__
password = pypi-YOUR-TOKEN-HERE
EOF

# 3. 发布
./scripts/publish-pypi.sh

# 4. 验证
pip install openclaw-quant-analyst
python3 -c "from openclaw_quant import __version__; print(f'Installed: {__version__}')"
```

#### 发布到 npm

```bash
# 1. 登录 npm
npm login

# 2. 发布
./scripts/publish-npm.sh

# 3. 验证
npm install -g openclaw-quant-analyst
openclaw-quant-analyst help
```

## 📊 发布后验证

### PyPI
- [ ] 访问: https://pypi.org/project/openclaw-quant-analyst/
- [ ] 测试安装: `pip install openclaw-quant-analyst`
- [ ] 检查文档显示正确

### npm
- [ ] 访问: https://www.npmjs.com/package/openclaw-quant-analyst
- [ ] 测试安装: `npm install -g openclaw-quant-analyst`
- [ ] 测试 CLI: `openclaw-quant-analyst help`

### GitHub
- [ ] 创建 Release: `git tag v0.1.0 && git push --tags`
- [ ] 更新 README 添加安装徽章

### ClawHub
- [ ] 更新 skill: `clawhub publish quant-analyst --version 0.1.0`

## 🎯 当前状态

```
✅ 代码已提交到 GitHub
✅ 发布脚本已准备
✅ 包配置已完成
⏳ 等待发布到 PyPI
⏳ 等待发布到 npm
```

## 💡 发布命令速查

```bash
# 快速发布（两个平台）
./scripts/publish-all.sh

# 仅 PyPI
./scripts/publish-pypi.sh

# 仅 npm
./scripts/publish-npm.sh

# 测试安装
pip install openclaw-quant-analyst
npm install -g openclaw-quant-analyst
```

## ⚠️ 注意事项

1. **版本号不能重复**: PyPI 不允许覆盖已发布的版本
2. **npm 需要登录**: 运行 `npm login` 并验证
3. **首次发布**: 确保包名 `openclaw-quant-analyst` 未被占用
4. **测试环境**: 建议先在 test.pypi.org 测试

## 🐛 常见问题

### PyPI: "File already exists"
- 解决：增加版本号

### npm: "You do not have permission"
- 解决：`npm login` 并检查权限

### "Package name taken"
- 检查: `pip search openclaw-quant-analyst`
- 检查: `npm view openclaw-quant-analyst`
- 如已存在，选择新名字或联系所有者
