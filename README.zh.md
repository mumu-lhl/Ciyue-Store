# Ciyue-Store

[English](README.md) | [简体中文](README.zh.md)

[词悦（Ciyue）](https://github.com/mumu-lhl/Ciyue) 的官方资源商店清单仓库，用于收录并分发**授权合法**的词典、Hunspell 词形数据与语音包。

## 清单格式说明（`catalog.yaml`）

`catalog.yaml` 采用 YAML 格式，顶层结构如下：

```yaml
schemaVersion: 1
items:
  - ...
```

### 条目字段说明

| 字段 | 类型 | 必填 | 说明 |
| :--- | :--- | :--- | :--- |
| `id` | string | 是 | 全局唯一小写标识（正则：`^[a-z0-9][a-z0-9_-]*$`）。 |
| `type` | string | 是 | 资源类型：`dictionary`（词典）、`hunspell` 或 `audio`（语音包）。 |
| `name` | string | 是 | 商店中展示的名称。 |
| `description` | string | 否 | 简介（支持 YAML 多行文本 `\|`）。 |
| `author` | string | 是 | 作者或维护者名称。 |
| `license` | string | 是 | 授权协议（如 `MIT`、`GPL-3.0`、`CC-BY-SA-4.0`）。 |
| `sourceUrl` | string | 是 | 资源上游主页或仓库地址（`http://` 或 `https://`）。 |
| `languages` | list[string] | 否 | 语言代码列表（如 `["en", "zh"]`、`["ja"]`）。 |
| `format` | string | 是 | 格式标识：`mdx`、`stardict`、`zim`、`hunspell`、`audio_mdd`、`audio_zip` 或 `audio_zips`。 |
| `extract` | bool | 否 | 下载后是否解压 `.zip` 压缩包，默认 `false`（语音包 `audio_zip`/`audio_zips` 与直链 `.aff`/`.dic` 保持 `false`；词典压缩包设为 `true`）。 |
| `source` | object | 是 | 下载来源配置（见下文）。 |

### 来源类型（`source`）

#### 1. `github_release`

从 GitHub Release 下载匹配的资产文件（默认获取最新 Release，也可通过 `tag` 指定版本）：

```yaml
source:
  type: github_release
  repo: owner/repo
  # tag: v1.0.0          # 可选；不填则拉取 latest release
  assetPattern: "*.zip"  # 支持通配符，或使用 `assets: [file.zip]`
```

#### 2. `github_raw`

直接从 GitHub 仓库分支拉取指定文件：

```yaml
source:
  type: github_raw
  repo: owner/repo
  branch: main           # 可选；默认 "main"
  files:
    - zh_CN.aff
    - zh_CN.dic
```

#### 3. `direct`

从 HTTP/HTTPS 直链下载单个或多个文件：

```yaml
source:
  type: direct
  url: https://example.com/en_us.zips
```

需要同时下载多个文件并指定文件名时：

```yaml
source:
  type: direct
  files:
    - url: https://example.com/dict.mdx
      filename: dict.mdx
    - url: https://example.com/dict.mdd
      filename: dict.mdd
```

## 分支与同步流程

- **`dev`**：日常提交与接收 PR 的默认分支。
- **`main`**：面向词悦客户端的生产分支，受 Branch Ruleset 保护禁止直接推送；`.github/workflows/sync-main.yml` 会在 `dev` 通过全部校验后自动创建 `dev -> main` 的 PR 完成同步。

## 本地校验

使用 [uv](https://docs.astral.sh/uv/) 运行校验与单元测试：

```bash
uv run --with pyyaml python scripts/validate_catalog.py catalog.yaml
uv run --with pyyaml python -m unittest discover -s scripts -p "test_*.py" -v
```
