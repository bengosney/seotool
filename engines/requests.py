from requests import get

from engines import engine, response


class requests(engine):
    async def get(self, url: str, **kwargs) -> response:
        requests_response = get(url, **kwargs)

        return requests._convert_response(requests_response)

    @staticmethod
    def _convert_response(requests_response) -> response:
        return response(
            headers=requests_response.headers,
            status_code=requests_response.status_code,
            url=requests_response.url,
            body=requests_response.text,
        )
