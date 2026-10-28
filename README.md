# myscheduleapp-release

排班 App 的**发布仓库**：只放三个文件，**不含任何源码**。

| 文件 | 用途 |
|---|---|
| `version.json` | 远程更新清单（App 启动时读取，比对 versionCode） |
| `plans.json` | 作业计划快照（App 每天 12:00 / 17:00 定点比对） |
| `app-release.apk` | 最新安装包（App 内下载后校验 sha256 / 包名 / 版本 / 签名） |

- 源码仓库：`xh-like/myscheduleapp`（私有）
- 备用通道：`https://schedule-plans.app.workbuddy.host`（GitHub 不可达时 App 自动回退）

更新流程：改 `app/build.gradle.kts` 的版本号 → `gradle assembleRelease` → 覆盖 `app-release.apk` →
同步 `version.json` 的 versionCode / versionName / size / sha256 / notes → commit。
