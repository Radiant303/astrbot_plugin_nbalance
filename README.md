# astrbot_plugin_nbalance

AstrBot 插件 - 查询 NewAPI 用户余额

## 简介

本插件用于在 AstrBot 中查询 NewAPI 用户的余额信息，支持命令行查询和 LLM 工具调用两种方式。

## 致谢

感谢 [BUGJI/astrbot_plugin_balance](https://github.com/BUGJI/astrbot_plugin_balance) 提供的项目参考和灵感。

## 功能特性

- ✅ 通过 `/余额` 命令快速查询余额
- ✅ 通过自然语言 LLM 工具调用查询余额

## 安装

1. 将本插件放入 AstrBot 的 `plugins` 目录
2. 重启 AstrBot 或重载插件

## 配置

在 AstrBot 配置文件中添加以下配置项：

```json
{
  "api_config": "https://your-newapi.com",// NewAPI 接口地址
  "userid": "10001",// 用户ID
  "token": "your-api-token",// 系统令牌
  "enable_llm_tool": false// 是否启用 LLM 工具
}