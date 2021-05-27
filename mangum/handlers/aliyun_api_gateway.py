import base64
import urllib.parse
from typing import Dict, Any, TYPE_CHECKING

from .abstract_handler import AbstractHandler
from .. import Response, Request


class AliyunApiGateway(AbstractHandler):
    """
    Handles Aliyun API Gateway events, transforming them into ASGI Scope and handling
    responses
    """

    TYPE = "ALIYUN_API_GATEWAY"

    def __init__(
        self,
        trigger_event: Dict[str, Any],
        trigger_context: "LambdaContext",
        base_path: str = "/",
        **kwargs: Dict[str, Any],  # type: ignore
    ):
        super().__init__(trigger_event, trigger_context, **kwargs)
        self.base_path = base_path

    @property
    def request(self) -> Request:
        event = self.trigger_event

        if event.get("headers"):
            headers = {k.lower(): v for k, v in event.get("headers", {}).items()}
        else:
            headers = {}

        source_ip = None  # TODO - this requires getting based on system parameters

        path = event["path"]
        http_method = event["httpMethod"]

        if event.get("queryParameters"):
            query_string = urllib.parse.urlencode(
                event.get("queryParameters", {})
            ).encode()
        else:
            query_string = b""

        # TODO - add support for extracting CaDomain and CaHttpSchema
        server_name = headers.get("host", "mangum")
        server_port = 80
        server = (server_name, int(server_port))
        client = (source_ip, 0)

        if not path:
            path = "/"
        elif self.base_path and self.base_path != "/":
            if not self.base_path.startswith("/"):
                self.base_path = f"/{self.base_path}"
            if path.startswith(self.base_path):
                path = path[len(self.base_path) :]

        return Request(
            method=http_method,
            headers=[[k.encode(), v.encode()] for k, v in headers.items()],
            path=urllib.parse.unquote(path),
            scheme=headers.get("x-forwarded-proto", "https"),
            query_string=query_string,
            server=server,
            client=client,
            trigger_event=self.trigger_event,
            trigger_context=self.trigger_context,
            event_type=self.TYPE,
        )

    @property
    def body(self) -> bytes:
        body = self.trigger_event.get("body", b"") or b""

        if self.trigger_event.get("isBase64Encoded", False):
            return base64.b64decode(body)
        if not isinstance(body, bytes):
            body = body.encode()

        return body

    def transform_response(self, response: Response) -> Dict[str, Any]:
        headers, _ = self._handle_multi_value_headers(
            response.headers
        )

        body, is_base64_encoded = self._handle_base64_response_body(
            response.body, headers
        )

        return {
            "statusCode": response.status,
            "headers": headers,
            "body": body,
            "isBase64Encoded": is_base64_encoded,
        }
