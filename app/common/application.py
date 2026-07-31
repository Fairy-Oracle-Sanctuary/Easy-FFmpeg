import sys
import traceback

from PySide6.QtCore import QIODevice, QSharedMemory, Signal
from PySide6.QtNetwork import QLocalServer, QLocalSocket
from PySide6.QtWidgets import QApplication

from .event_bus import event_bus
from .logger import Logger


class SingletonApplication(QApplication):
    """Singleton application"""

    messageSig = Signal(object)
    logger = Logger("application")

    def __init__(self, argv: list[str], key: str):
        super().__init__(argv)
        self.key = key
        self.timeout = 1000
        self.server = QLocalServer(self)

        # cleanup (only needed for unix)
        QSharedMemory(key).attach()
        self.memory = QSharedMemory(self)
        self.memory.setKey(key)

        if self.memory.attach():
            self.isRunning = True

            self.sendMessage(" ".join(argv[1:]) if len(argv) > 1 else "show")
            sys.exit()

        self.isRunning = False
        if not self.memory.create(1):
            self.logger.error(self.memory.errorString())
            raise RuntimeError(self.memory.errorString())

        self.server.newConnection.connect(self.__onNewConnection)
        QLocalServer.removeServer(key)
        self.server.listen(key)

    def __onNewConnection(self):
        socket = self.server.nextPendingConnection()
        if socket.waitForReadyRead(self.timeout):
            event_bus.appMessageSig.emit(socket.readAll().data().decode("utf-8"))
            socket.disconnectFromServer()

    def sendMessage(self, message: str):
        """send message to another application"""
        if not self.isRunning:
            return

        # connect to another application
        socket = QLocalSocket(self)
        socket.connectToServer(self.key, QIODevice.WriteOnly)
        if not socket.waitForConnected(self.timeout):
            self.logger.error(socket.errorString())
            return

        # send message
        socket.write(message.encode("utf-8"))
        if not socket.waitForBytesWritten(self.timeout):
            self.logger.error(socket.errorString())
            return

        socket.disconnectFromServer()


def exception_hook(exception: BaseException, value, tb):
    """exception callback function"""
    SingletonApplication.logger.error("Unhandled exception", (exception, value, tb))
    message = "\n".join(
        ["".join(traceback.format_tb(tb)), f"{exception.__name__}: {value}"]
    )
    event_bus.appErrorSig.emit(message)


sys.excepthook = exception_hook
