import abc
from typing import Any


class BaseMemory(abc.ABC):
    """
    Abstract interface for independent AI Memory management.
    """

    @abc.abstractmethod
    async def get_context(self, key: str, **kwargs: Any) -> list[dict[str, str]]:
        """
        Retrieve structured memory context/messages associated with the key.
        """
        pass

    @abc.abstractmethod
    async def store(self, key: str, data: Any, **kwargs: Any) -> None:
        """
        Append or save new data to memory key.
        """
        pass

    @abc.abstractmethod
    async def clear(self, key: str) -> None:
        """
        Evict or reset memory associated with key.
        """
        pass
