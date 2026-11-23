# 随便记

个人记录管理器,支持账号密码、想法记录、钱包地址、AI 提示词四类数据。使用 Fernet 对称加密本地存储,主密码由 PBKDF2 派生,可选一天内免密登录。

## 功能特性

- 数据分类管理
  - 账号密码:支持类型(邮箱/视频/论坛/社交/购物/工作/其他,可在设置中自定义)、网站、用户名、密码、网址、备注、TOTP 两步验证密钥
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
  - 按分类字段下拉筛选(账号按类型、想法按标签、钱包按类型、提示词按分类,与搜索叠加生效)
  - 点击表头排序(升序/降序切换,切换分类自动复位)
  - 右键菜单快速复制字段(账号密码仅保留复制用户名/密码)
  - 设置内「备份」页:立即备份、查看历史备份、选择恢复(恢复前自动另存当前数据)
  - 密码生成器(20 位随机,可显示/隐藏)+ 实时强度提示
- 界面
  - PyQt6「纸间 · Paperlight」主题
  - 米白纸面 + 墨绿点缀,252px 浅色侧边栏
  - 线性单色图标、白色胶囊导航、细描边表格卡片
  - 选中记录右侧显示详情面板,每个字段可单独复制
  - 填了 TOTP 密钥的账号,详情面板实时显示 6 位验证码与剩余秒数(30 秒滚动),可一键复制
  - 窗口位置、列宽、上次分类自动记忆
- 效率入口
  - `Ctrl+K` 全局搜索:跨四个分类查找,选中后跳到对应记录
  - 托盘常驻:关闭窗口收进托盘,双击托盘图标恢复
  - 全局热键快速记录:默认 `Ctrl+Alt+Space`,被占用时自动退到 `Ctrl+Shift+Space` / `Ctrl+Alt+J`;唤出「记一笔」小窗,回车直接存成一条想法(全部占用时托盘菜单仍可用)
- 快捷键
  - `Ctrl+N` 新增、`Ctrl+F` 搜索、`Ctrl+K` 全局搜索、`Esc` 清空搜索、`Ctrl+L` 锁定
  - 表格内:`Enter` 编辑、`Delete` 删除、`Ctrl+C` 复制主字段(账号为密码)

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

产物是 onedir 文件夹 `dist/随便记/`:分发时要连同 `_internal/` 一起拷贝,EXE 不能单独拿走。

启动耗时:onedir 相对旧的 onefile 省去每次启动把 40MB 解压到临时目录的过程,实测冷启动从约 1.6 秒降到约 0.6 秒(同一台机器、同一份数据、二次启动)。

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
