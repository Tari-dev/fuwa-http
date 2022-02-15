import sys
from typing import (
    Any,
    Dict,
    List,
    Optional,
    ClassVar,
    Union
)
from contextlib import suppress as supress_exc

import aiohttp

from . import __version__
from .errors import (
    HTTPException,
    NotFound,
    TooManyRequests,
    InternalServerError,
    Forbidden
)


class Route:
    BASE: ClassVar[str] = "https://discord.com/api/v10"

    def __init__(
        self,
        method: str,
        path: str,
        **params
    ):
        path = path.format(**params)

        self.method = method
        self.path = path
        self.url = self.BASE + path

class HTTPClient:
    def __init__(
        self,
        token: str,
        **session_options
    ):
        self.token = token
        self.session_opts = session_options

        user_agent = "DiscordApplication (https://github.com/fuwa-py/fuwa-http {0}) Python/{1.major}{1.minor} aiohttp/{2}"
        self.user_agent = user_agent.format(
            __version__,
            sys.version_info,
            aiohttp.__version__
        )

        self.application_data: Optional[dict] = None

        self.__session: Optional[aiohttp.ClientSession] = None

    def share_session(self, session: aiohttp.ClientSession):
        self.__session = session

    async def init(self):
        """Fills in necessary information such as
        the application id, etc. This information is vital for certain endpoints
        """

        route = Route("GET", "/oauth2/applications/@me")
        data = await self.request(route)
        self.application_data = data

    async def request(
        self,
        route: Route,
        **kwargs
    ):
        url = route.url
        method = route.method

        # Header creation
        headers = kwargs.pop("headers", {})
        headers["Authorization"] = "Bot " + self.token
        headers["User-Agent"] = self.user_agent

        if "json" in headers:
            headers["Content-Type"] = "application/json"

        kwargs["headers"] = headers

        # Check if the session exists, if not, create one
        if not self.__session:
            opts = self.session_opts
            self.__session = aiohttp.ClientSession(**opts)

        async with self.__session.request(method, url, **kwargs) as r:
            data = await self.read_response(r)

            if not r.ok:
                if r.status == 404:
                    raise NotFound(r, data)
                elif r.status in {500, 501, 502, 503, 504}:
                    raise InternalServerError(r, data)
                elif r.status == 403:
                    raise Forbidden(r, data)
                elif r.status == 429:
                    raise TooManyRequests(r, data)
                else:
                    raise HTTPException(r, data)

        return data

    async def close(self):
        with supress_exc(Exception):
            await self.__session.close()

    async def read_response(self, response: aiohttp.ClientResponse) -> Union[bytes, dict]:
        headers = response.headers
        try:
            if headers["content-type"].lower() == "application/json":
                return await response.json()
            else:
                return await response.text()
        except KeyError:
            # Thanks cloudflare
            return await response.text()

    async def bulk_upsert_application_commands(
        self,
        commands: List[Dict[str, Any]],
        *,
        guild_id: Optional[int] = None
    ):
        # "/applications/<my_application_id>/commands"
        application_id = self.application_data["id"]
        route = Route("PUT", "/applications/{application_id}/commands", application_id=application_id)

        if guild_id:
            route = Route(
                "PUT",
                "/applications/{application_id}/guilds/{guild_id}/commands",
                application_id=application_id,
                guild_id=guild_id
            )

        data = await self.request(route, json=commands)
        return data

    async def create_interaction_response(
        self,
        callback_type: int,
        interaction_id: int,
        interaction_token: str,
        *,
        data: Optional[dict] = None
    ):
        route = Route(
            "POST",
            "/interactions/{interaction_id}/{interaction_token}/callback",
            interaction_id=interaction_id,
            interaction_token=interaction_token
        )

        payload = {
            "type": callback_type
        }
        if data:
            payload["data"] = data
        
        data = await self.request(route, json=payload)
        return data
