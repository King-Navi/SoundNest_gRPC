import threading
import os
from pathlib import Path

class BaseResourceManager:
    def __init__(self, base_dir):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.locks : dict = {}
        self.locks_lock = threading.Lock()

    def _get_lock(self, resource_key : tuple):
        with self.locks_lock:
            if resource_key not in self.locks:
                self.locks[resource_key] = threading.Lock()
            return self.locks[resource_key]

    def _get_resource_key(self, resource_id: tuple) -> tuple:
        return resource_id

    def _get_file_path(self, resource_id: tuple) -> Path:
        """
        This method must be implemented in subclasses.
        Should return a pathlib.Path object for the file path.
        """
        raise NotImplementedError("Subclasses must implement _get_file_path")

    def read_resource(self, resource_id: tuple, binary=True)-> bytes|str:
        resource_key = self._get_resource_key(resource_id)
        lock = self._get_lock(resource_key)
        mode = "rb" if binary else "r"

        with lock:
            try:
                path = self._get_file_path(resource_id)
                with open(path, mode) as f:
                    return f.read()
            except IOError as e:
                raise e

    def write_resource(self, resource_id: tuple, data, binary=True):
        resource_key = self._get_resource_key(resource_id)
        lock = self._get_lock(resource_key)
        mode = "wb" if binary else "w"

        with lock:
            try:
                path = self._get_file_path(resource_id)
                os.makedirs(path.parent, exist_ok=True)
                with open(path, mode) as f:
                    f.write(data)
            except IOError as e:
                raise e