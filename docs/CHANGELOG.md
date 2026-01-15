# 变更日志

本文档记录项目的所有重要变更。遵循 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/) 规范。

## [2025-12-30] - Docker 一键部署支持

### 变更
- 添加 Docker 一键部署支持
- 创建 Dockerfile（多阶段构建）
- 创建 docker-compose.yml 配置文件
- 创建部署指南文档
- 支持跨平台部署（Linux、macOS、Windows）

### 原因
- 简化部署流程，无需手动配置环境
- 确保环境一致性，避免依赖问题
- 支持跨平台部署，提高可用性
- 便于快速启动和使用

### 影响
- 部署方式：新增 Docker 部署选项（推荐）
- 用户体验：大幅简化部署流程
- 维护性：环境配置统一，易于维护

### 文档更新
- [docs/guides/DEPLOYMENT.md] - 部署指南（新建）
- [Dockerfile] - Docker 镜像构建文件（新建）
- [docker-compose.yml] - Docker Compose 配置（新建）
- [.dockerignore] - Docker 忽略文件（新建）
- [scripts/docker-setup.sh] - Docker 快速设置脚本（新建）
- [README.md] - 添加 Docker 部署说明
- [docs/architecture/ARCHITECTURE.md] - 添加部署方案章节
- [.gitignore] - 更新忽略规则

### 部署特性

**Docker 配置：**
- 多阶段构建，优化镜像大小
- 自动安装所有依赖（Python、FFmpeg 等）
- 数据持久化（输出目录、缓存目录）
- 环境变量配置支持
- 健康检查支持

**一键部署命令：**
```bash
docker-compose up -d
```

## [2025-12-30] - Cursor 规则文件标准化

### 变更
- 将 `.cursorrules` 文件转换为 Cursor 标准格式
- 创建 `.cursor/rules/` 目录结构
- 将规则拆分为多个主题文件：
  - `documentation-driven-development.md` - 文档驱动开发核心规则
  - `documentation-organization.md` - 文档组织规则
  - `coding-standards.md` - 编码规范
  - `ai-assistant-behavior.md` - AI 助手行为规范

### 原因
- 符合 Cursor IDE 的标准规则文件格式
- 提高规则的可维护性和可读性
- 支持按主题组织规则，便于管理

### 影响
- Cursor AI 助手将自动读取 `.cursor/rules/` 目录下的规则
- 规则文件结构更清晰，便于维护

### 文档更新
- [.cursor/rules/documentation-driven-development.md] - 文档驱动开发规则（新建）
- [.cursor/rules/documentation-organization.md] - 文档组织规则（新建）
- [.cursor/rules/coding-standards.md] - 编码规范规则（新建）
- [.cursor/rules/ai-assistant-behavior.md] - AI 助手行为规范（新建）
- [.cursorrules] - 已删除（替换为标准格式）

## [2025-12-30] - 文档重组和规范建立

### 变更
- 重组文档结构，建立 docs/ 目录体系
- 创建 Cursor MDC 规则文件
- 建立文档驱动开发规范
- 创建编码规范文档
- 创建变更日志 (CHANGELOG.md)

### 原因
- 建立清晰的文档组织结构
- 规范开发流程，确保文档与代码同步
- 实现"文档即系统"的开发理念

### 影响
- 文档组织结构
- 开发工作流程
- AI 助手行为规范

### 文档更新
- [CHANGELOG.md] - 变更日志（新建）
- [docs/README.md] - 文档目录索引（新建）
- [docs/development/CODING_STANDARDS.md] - 编码规范（新建）
- [README.md] - 更新文档链接

### 文档重组详情

**移动的文档：**
- `ARCHITECTURE.md` → `docs/architecture/ARCHITECTURE.md`
- `DESIGN_PRINCIPLES.md` → `docs/architecture/DESIGN_PRINCIPLES.md`
- `IMPLEMENTATION.md` → `docs/architecture/IMPLEMENTATION.md`
- `PROJECT_PLAN.md` → `docs/development/PROJECT_PLAN.md`

**保留在根目录的文档：**
- `README.md` - 项目入口文档
- `CHANGELOG.md` - 变更日志

## [2025-12-30] - 项目初始化

### 变更
- 初始化项目结构
- 创建架构设计文档
- 建立文档驱动开发规范

### 原因
- 启动 Smart Video 项目，需要清晰的架构设计和开发规范
- 建立文档即系统的开发理念

### 影响
- 项目结构
- 开发流程
- 文档组织

### 文档更新
- [docs/architecture/ARCHITECTURE.md] - 系统架构设计
- [docs/architecture/DESIGN_PRINCIPLES.md] - 设计原则（不保存视频文件）
- [docs/architecture/IMPLEMENTATION.md] - 实现细节
- [docs/development/PROJECT_PLAN.md] - 项目开发计划

### 设计决策

#### 不保存视频文件
- **决策**：只下载字幕，不下载视频文件
- **原因**：节省存储空间，用户可通过 URL 查看原视频
- **影响**：所有下载和处理逻辑都基于这一原则
- **文档**：详见 `docs/architecture/DESIGN_PRINCIPLES.md`

#### 文档驱动开发
- **决策**：文档是系统的真实来源，代码只是实现
- **原因**：保持系统可理解、可维护
- **影响**：所有改动必须先更新文档
- **文档**：详见 `.cursor/rules/documentation-driven-development.md`

