import aiohttp, logging
from typing import Dict, Optional, Any, Callable, Tuple


LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)
LOGGER.addHandler(handler := logging.FileHandler(f"{__name__}.log"))
handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))


class Requester:
    def __init__(self, base_url: str, headers: Optional[Dict] = None) -> None:
        self.URL = base_url
        self.HEADERS = headers
        self._client = aiohttp.ClientSession(self.URL, headers=self.HEADERS)

    async def __aenter__(self) -> "Requester":
        return self

    async def __aexit__(self, *args) -> None:
        await self._client.close()

    async def _request(
        self, method: Callable, endpoint: str, data: Optional[Dict] = None
    ) -> Tuple[int, Any]:
        try:
            response: aiohttp.ClientResponse = await method(f"/{endpoint}", json=data)
            log_str = f"{response.status} {response.real_url}"
            if response.status == 200:
                LOGGER.info(log_str)
            else:
                LOGGER.warning(log_str)
            try:
                result = await response.json()
            except Exception as err:
                LOGGER.exception(err)
                result = await response.text()
        except Exception as err:
            LOGGER.exception(err)
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
