# 随便记

个人记录管理器,支持账号密码、想法记录、钱包地址、AI 提示词四类数据。使用 Fernet 对称加密本地存储,主密码由 PBKDF2 派生,可选一天内免密登录。

## 功能特性

- 数据分类管理
  - 账号密码:支持类型(邮箱/视频/论坛/社交/购物/工作/其他,可在设置中自定义)、网站、用户名、密码、网址、备注
  - 想法记录:标题、内容、标签
  - 钱包地址:名称、地址、类型、备注
  - AI 提示词:标题、内容、分类
- 主密码保护
  - PBKDF2-SHA256 派生密钥,600,000 次迭代
  - 数据原子写入 + 自动备份
  - 每次保存生成滚动备份(保留 7 份),主文件损坏可自动恢复
  - 支持在设置中修改主密码,改密过程带 journal 回滚
  - 可选一天内免密登录(使用系统钥匙串保存主密码)
  - 闲置 10 分钟自动锁定,`Ctrl+L` 立即锁定,锁定后清空内存中的记录
  - 复制密码 25 秒后自动清空剪贴板(仅清除自己写入的内容)
- 数据操作
  - 添加、编辑、删除
  - 搜索过滤
  - 账号密码支持按类型下拉筛选(与搜索叠加生效)
  - 右键菜单快速复制字段(账号密码仅保留复制用户名/密码)
- 界面
  - PyQt6「纸间 · Paperlight」主题
  - 米白纸面 + 墨绿点缀,252px 浅色侧边栏
  - 线性单色图标、白色胶囊导航、细描边表格卡片

## 运行环境

- Python 3.10+
- Windows / macOS / Linux

## 数据目录

启动时按以下顺序定位,不再依赖当前工作目录(从快捷方式、任务栏启动也能找到同一个库):

1. 环境变量 `SUIBIANJI_DATA_DIR` 指定的目录
2. 程序所在目录旁的 `data/`(便携模式,已有安装会沿用原目录)
3. `%APPDATA%\Suibianji\data`(安装目录不可写时自动回退)

程序「设置 → 常规」里会显示当前数据目录,并可一键打开。

## 安装依赖

```bash
pip install -r requirements.txt
```

依赖列表:

- `cryptography>=41.0.0`
- `PyQt6>=6.6.0`
- `keyring>=25.0.0`

## 运行应用

```bash
python -m suibianji
```

也可以直接运行 `python src/run_suibianji.py`(打包入口),或安装后使用 `suibianji` 命令。

## 开发

```bash
python -m venv .venv
.venv\Scripts\activate            # Windows
pip install -r requirements-lock.txt
pip install -e . --no-deps
pytest
ruff check src tests
```

依赖以 `requirements-lock.txt` 为准(锁定版本,可复现构建);`requirements.txt` 只声明直接依赖的最低版本。

## 打包为可执行文件

确保已安装 PyInstaller:

```bash
pip install pyinstaller
```

在项目根目录执行:

```bash
pyinstaller suibianji.spec
```

打包产物位于 `dist/随便记.exe`(Windows)或对应平台的可执行文件。

## 项目结构

```
随便记/
├── src/
│   ├── suibianji/
│   │   ├── __main__.py          # 入口:日志、旧数据导入、登录流程
│   │   ├── core/                # 模型、加密存储、设置、路径、单实例
│   │   └── ui/                  # 主题与控件、主窗口与对话框、图标
│   ├── run_suibianji.py         # PyInstaller 打包入口
│   └── main_qt6_redesigned.py   # 旧入口兼容 shim(保留一个版本周期)
├── tests/                       # pytest 用例(核心逻辑 + 单实例 + 路径)
├── docs/优化任务方案.md         # 迭代计划与任务编号
├── .github/workflows/ci.yml     # Windows 上跑 lint、测试、打包
├── data/                        # 运行时数据目录(默认同级,见上文定位规则)
├── suibianji.spec               # PyInstaller 打包配置
├── requirements.txt             # 直接依赖
├── requirements-lock.txt        # 锁定版本(CI 与本地开发使用)
└── README.md
```

## 数据安全说明

1. 主密码是解密数据的唯一凭证,忘记主密码将无法恢复数据。
2. 主密码以派生密钥形式参与加密,应用本身不保存明文主密码。
3. 开启“一天内免密登录”后,主密码会存入系统钥匙串(Windows Credential Locker / macOS Keychain / Linux Secret Service),关闭设置中的开关会立即清除。
4. 建议定期备份 `data/records.enc.bak` 或整个 `data/` 目录。

## 许可证

MIT
