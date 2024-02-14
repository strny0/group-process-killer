from typing import Callable, Set
import asyncio
import getpass

from pyngrok import ngrok  # type: ignore[import-untyped]
import websockets as ws
import keyboard
import psutil


def find_procs_by_name(name):
    """Return a list of processes matching 'name'."""
    for proc in psutil.process_iter(["name"]):
        try:
            if name.lower() in proc.info["name"].lower():  # type: ignore
                yield proc
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass


def kill_process(name: str):
    for proc in find_procs_by_name(name):
        print(f"Killing process {proc}")
        proc.kill()


# Just echoes commands to all clients
class Server:
    def __init__(self, port: int) -> None:
        self.port = port
        self.clients: Set[ws.WebSocketServerProtocol] = set()

        ngrok.install_ngrok()
        self.tunnel = ngrok.connect(addr=f"localhost:{self.port}", proto="tcp")
        print("Started ngrok tunnel")
        print(self.tunnel)

    async def serve(self):
        async with ws.serve(self.handler, "localhost", self.port):
            await asyncio.Future()

    async def handler(self, websocket: ws.WebSocketServerProtocol):
        self.clients.add(websocket)
        try:
            async for message in websocket:
                print(f"[{websocket.remote_address[0]}] {message!r}")
                for client in self.clients:
                    if client != websocket:
                        await client.send(message)
        except ws.ConnectionClosedError:
            print(f"[{websocket.remote_address[0]}] CONNECTION CLOSED")
        finally:
            self.clients.remove(websocket)


class Client:
    def __init__(
        self,
        url: str,
        on_trigger: Callable | None = None,
        trigger_word: str = "KILL",
        trigger: str = "ctrl+r",
        loop=asyncio.get_event_loop(),
    ) -> None:
        self.loop = loop
        self.url = url
        self.send_queue: asyncio.Queue[ws.Data] = asyncio.Queue(maxsize=100)
        self.on_trigger = on_trigger
        self.trigger_word = trigger_word

        keyboard.add_hotkey(trigger, self.send, args=())

    async def connect(self):
        print("Connecting...")

        async with ws.connect(self.url) as websocket:
            print("Connected...")
            recv_task = self.recv_task(websocket)
            send_task = self.send_task(websocket)
            await asyncio.gather(recv_task, send_task)

    async def recv_task(self, websocket: ws.WebSocketClientProtocol):
        print("Starting recv task")
        async for message in websocket:
            print(f"Client received message: {message!r}")
            if message == self.trigger_word:
                self.on_trigger() if self.on_trigger is not None else ()

    async def _send(self):
        await self.send_queue.put(f"KILL")
        self.on_trigger() if self.on_trigger is not None else ()

    def send(self):
        asyncio.run_coroutine_threadsafe(self._send(), self.loop)

    async def send_task(self, websocket: ws.WebSocketClientProtocol):
        print("Starting send task")
        await websocket.send(f"Announcing connection from {getpass.getuser()}")

        while True:
            try:
                command = await self.send_queue.get()
                print(f"Sending command: {command!r}")
                await websocket.send(command)
                self.send_queue.task_done()
            except asyncio.QueueEmpty:
                ...
