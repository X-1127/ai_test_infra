# -*- mode: python ; coding: utf-8 -*-

import sys
import os
from pathlib import Path
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

# 项目根目录 - 使用 sys.argv[0] 获取 spec 文件路径
spec_file = Path(sys.argv[0]).resolve()
project_root = spec_file.parent

# 收集所有需要的数据文件
datas = [
    (str(project_root / 'config' / 'responses.yaml.example'), 'config'),
    (str(project_root / 'scripts' / 'start_server.py'), 'scripts'),
]

# 收集所有需要的隐藏导入
hiddenimports = [
    'PyQt6',
    'PyQt6.QtCore',
    'PyQt6.QtGui',
    'PyQt6.QtWidgets',
    'fastapi',
    'fastapi.routing',
    'fastapi.middleware',
    'fastapi.middleware.cors',
    'uvicorn',
    'uvicorn.logging',
    'uvicorn.loops',
    'uvicorn.loops.auto',
    'uvicorn.protocols',
    'uvicorn.protocols.http',
    'uvicorn.protocols.http.auto',
    'uvicorn.protocols.websockets',
    'uvicorn.lifespan',
    'uvicorn.lifespan.on',
    'uvicorn.server',
    'pydantic',
    'pydantic_settings',
    'pydantic_core',
    'pyyaml',
    'httpx',
    'httpx._transports.default',
    'httpx._transports.http2',
    'starlette',
    'starlette.applications',
    'starlette.routing',
    'starlette.middleware',
    'starlette.responses',
    'starlette.types',
    'app',
    'app.main',
    'app.config',
    'app.models',
    'app.api.chat',
    'app.api.logs',
    'app.services.mock_service',
    'app.services.response_config_manager',
    'app.services.log_manager',
    'desktop',
    'desktop.main',
    'desktop.config.settings',
    'desktop.services.api_client',
    'desktop.services.server_manager',
    'desktop.ui.main_window',
    'desktop.ui.server_tab',
    'desktop.ui.config_tab',
    'desktop.ui.logs_tab',
    'desktop.ui.test_tab',
    'desktop.ui.monitor_tab',
    'desktop.ui.rule_edit_dialog',
]

# 收集所有子模块
hiddenimports.extend(collect_submodules('app'))
hiddenimports.extend(collect_submodules('desktop'))

# 收集所有数据文件
datas.extend(collect_data_files('app'))
datas.extend(collect_data_files('desktop'))

# 确保包含所有必要的包
datas.extend(collect_data_files('fastapi'))
datas.extend(collect_data_files('uvicorn'))
datas.extend(collect_data_files('pydantic'))
datas.extend(collect_data_files('pydantic_settings'))
datas.extend(collect_data_files('starlette'))

# 排除不需要的模块
excludes = [
    'tkinter',
    'matplotlib',
    'numpy',
    'pandas',
    'scipy',
    'IPython',
    'notebook',
    'jupyter',
    'pytest',
    'black',
    'flake8',
    'mypy',
]

# 主配置
block_cipher = None

a = Analysis(
    ['desktop/main.py'],
    pathex=[str(project_root)],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=excludes,
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='LLM_Mock_Server',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,  # 临时启用控制台以查看错误信息
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=str(project_root / 'assets' / 'icon.ico') if (project_root / 'assets' / 'icon.ico').exists() else None,
)