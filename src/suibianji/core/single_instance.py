"""单实例守卫:第二个实例唤醒第一个,避免两个进程互相覆盖加密文件。

实现方式:每个数据目录对应一个本地套接字名,先尝试连接;
连上说明已有实例在跑,发送 activate 后自身退出;连不上则自己监听。
"""

import hashlib
from collections.abc import Callable

from PyQt6.QtCore import QObject
from PyQt6.QtNetwork import QLocalServer, QLocalSocket

CONNECT_TIMEOUT_MS = 400


def socket_name(data_dir) -> str:
    """按数据目录生成稳定的套接字名,不同数据目录可各开一个实例。"""
    digest = hashlib.sha256(str(data_dir).encode("utf-8")).hexdigest()[:16]
    return f"suibianji-{digest}"


class SingleInstanceGuard(QObject):
    def __init__(self, name: str, on_activate: Callable[[], None] | None = None, parent=None):
        super().__init__(parent)
        self._name = name
        self._on_activate = on_activate
        self._server: QLocalServer | None = None

    def acquire(self) -> bool:
        """返回 True 表示本进程是唯一实例;False 表示已通知并唤醒了旧实例。"""
        if self._notify_running_instance():
            return False
        # 只有确认无人监听时才清理残留套接字
        QLocalServer.removeServer(self._name)
        server = QLocalServer(self)
        server.newConnection.connect(self._handle_new_connection)
        if not server.listen(self._name):
            # 监听失败不阻断启动:宁可多开,也不能让用户打不开程序
            server.deleteLater()
            self._server = None
            return True
        self._server = server
        return True

    def _notify_running_instance(self) -> bool:
        sock = QLocalSocket()
        sock.connectToServer(self._name)
        if not sock.waitForConnected(CONNECT_TIMEOUT_MS):
            return False
        sock.write(b"activate")
        sock.flush()
        sock.waitForBytesWritten(CONNECT_TIMEOUT_MS)
        sock.disconnectFromServer()
        return True

    def _handle_new_connection(self):
        if self._server is None:
            return
        while self._server.hasPendingConnections():
            conn = self._server.nextPendingConnection()
            conn.disconnected.connect(conn.deleteLater)
            if self._on_activate is not None:
                self._on_activate()
