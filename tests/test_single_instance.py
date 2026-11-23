"""单实例守卫测试:第二个实例应被拒绝并唤醒第一个。"""
import os
import time
import uuid

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest


@pytest.fixture(scope="module")
def qapp():
    pytest.importorskip("PyQt6.QtWidgets")
    from PyQt6.QtWidgets import QApplication

    app = QApplication.instance() or QApplication([])
    yield app


def test_second_instance_is_rejected(qapp):
    from suibianji.core.single_instance import SingleInstanceGuard, socket_name

    name = socket_name(f"test-{uuid.uuid4()}")
    activated = []

    first = SingleInstanceGuard(name, lambda: activated.append(True))
    assert first.acquire() is True

    second = SingleInstanceGuard(name)
    assert second.acquire() is False

    # 等待事件循环处理连接
    for _ in range(25):
        qapp.processEvents()
        if activated:
            break
        time.sleep(0.02)
    assert activated == [True]
