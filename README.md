# Fuwa HTTP

The HTTP client implementation for the fuwa eco-system

### Example

```py
import asyncio

from fuwa.fhttp.client import HTTPClient


async def main():
    client = HTTPClient("bot token")
    await client.init() # calls the application info endpoint
    # this is necessary for most endpoints (such as application command
    # related endpoints)

    payload = [
        {
            "type": 1,
            "name": "hello",
            "description": "Hello, World!"
        }
    ]
    await client.bulk_upsert_application_commands(payload, guild_id=942837947315662859)
    await client.close()
    
loop = asyncio.get_event_loop()
loop.run_until_complete(main())
```

You may think this is quite verbose for a HTTP client, however, the fuwa eco-system doesn't expect you to usue this on its own. This package is used heavily within the `command-framework`. The package import (`from fuwa.fhttp`) is `fhttp` due to the `http` python standard library. This is to avoid any shadowing issues internally and for you.

Currently, the HTTPClient includes only 2 pre-built methods. These are very basic methods for slash commands. More will be coming soon.