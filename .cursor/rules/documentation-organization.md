# 文档组织规则

## 文档目录结构

```
smart-video/
├── README.md                    # 项目入口文档（保留在根目录）
├── CHANGELOG.md                 # 变更日志（保留在根目录）
├── docs/                        # 所有技术文档目录
│   ├── architecture/           # 架构文档
│   │   ├── ARCHITECTURE.md     # 系统架构设计
│   │   ├── DESIGN_PRINCIPLES.md # 设计原则
│   │   └── IMPLEMENTATION.md   # 实现细节
│   ├── development/            # 开发文档
│   │   ├── PROJECT_PLAN.md    # 项目计划
│   │   ├── CODING_STANDARDS.md # 编码规范
│   │   └── TESTING.md          # 测试文档
│   ├── api/                    # API 文档（未来）
│   └── guides/                 # 使用指南
│       └── USER_GUIDE.md       # 用户指南
└── src/                        # 源代码
```

## 文档分类规则

### 根目录文档（仅限）

- `README.md` - 项目入口，快速开始指南
- `CHANGELOG.md` - 变更日志（自动更新）
- `LICENSE` - 许可证文件
- `.gitignore`, `.env.example` 等配置文件

### docs/ 目录文档

- 所有技术文档、架构文档、开发文档
- 设计文档、实现细节、API 文档
- 使用指南、开发指南

## 文档模板

### CHANGELOG.md 格式

```markdown
# 变更日志

## [YYYY-MM-DD] - 变更类型

### 变更
- 简要描述改动内容

### 原因
- 为什么需要这个改动

### 影响
- 影响哪些模块
- 影响哪些功能

### 文档更新
- [docs/architecture/ARCHITECTURE.md] - 更新架构设计
- [docs/architecture/IMPLEMENTATION.md] - 更新实现细节

### 相关 Issue/PR
- #123
```

## 检查清单

每次提交代码前，检查：

- [ ] 已更新 CHANGELOG.md
- [ ] 已更新相关技术文档
- [ ] 已更新代码注释和文档字符串
- [ ] 文档与代码实现一致
- [ ] 所有文档链接有效
- [ ] 示例代码可运行
- [ ] 符合设计原则和编码规范

