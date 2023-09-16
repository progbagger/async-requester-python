import aiohttp, logging, asyncio
from typing import Dict, Optional, Any, Callable, Tuple, TextIO
import sys


class Requester:
    def __init__(
        self,
        base_url: Optional[str] = None,
        headers: Optional[Dict] = None,
        log: str | bool | TextIO = False,
    ) -> None:
        self.base_url = base_url
        self.LOGGER = logging.getLogger(__name__)
        self.LOGGER.setLevel(logging.DEBUG)
        self.URL = base_url
        self.HEADERS = headers
        self._client = aiohttp.ClientSession(self.URL, headers=self.HEADERS)
        try:
            handler = None
            if isinstance(log, bool) and log:
                handler = logging.FileHandler(f"{__name__}.log")
            elif isinstance(log, str):
                handler = logging.FileHandler(log)
            elif isinstance(log, bool) and not log:
                pass
            else:
                handler = logging.StreamHandler(log)
            if handler is not None:
                handler.setFormatter(
                    logging.Formatter("%(asctime)s %(levelname)s %(message)s")
                )
                self.LOGGER.addHandler(handler)
        except Exception:
            pass

    async def __aenter__(self) -> "Requester":
        return self

    async def __aexit__(self, *args) -> None:
        await self._client.close()

    async def _request(
        self, method: Callable, endpoint: str, data: Optional[Dict] = None
    ) -> Tuple[int, Any]:
        try:
            if not self.base_url:
                s = endpoint
            else:
                s = f"/{endpoint}"
            response: aiohttp.ClientResponse = await method(s, json=data)
            log_str = f"{response.status} {response.real_url}"
            if response.status == 200:
                self.LOGGER.info(log_str)
            else:
                self.LOGGER.warning(log_str)
            try:
                result = await response.json()
            except Exception:
                result = await response.text()
        except Exception as err:
            self.LOGGER.exception(err)
            raise err
        return response.status, result

    async def get(self, endpoint: str, data: Optional[Dict] = None) -> Tuple[int, Any]:
        return await self._request(self._client.get, endpoint, data)

    async def post(self, endpoint: str, data: Optional[Dict] = None) -> Tuple[int, Any]:
        return await self._request(self._client.post, endpoint, data)

    async def put(self, endpoint: str, data: Optional[Dict] = None) -> Tuple[int, Any]:
        return await self._request(self._client.put, endpoint, data)

    async def delete(
        self, endpoint: str, data: Optional[Dict] = None
    ) -> Tuple[int, Any]:
        return await self._request(self._client.delete, endpoint, data)


async def main():
    async with Requester(
        None,
        None,
        False,
    ) as requester:
        print(
            (
                await requester.get(
                    "https://stackoverflow.com/questions/63703237/proper-typing-for-sys-stdout-and-files/"
                )
            )[0]
        )


if __name__ == "__main__":
    asyncio.run(main())
