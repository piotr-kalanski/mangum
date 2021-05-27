import pytest

import urllib.parse

from mangum import Mangum
from mangum.handlers import AliyunApiGateway


def get_mock_aliyun_api_gateway_event(
    method, path, headers, query_parameters, path_parameters, body, body_base64_encoded
):
    return {
        "path": path,
        "httpMethod": method,
        "body": body,
        "isBase64Encoded": body_base64_encoded,
        "headers": headers,
        "queryParameters": query_parameters,
        "pathParameters": path_parameters,
    }

# TODO - more cases


@pytest.mark.parametrize(
    "method,path,headers,query_parameters,expected_query_string,path_parameters,"
    "body,body_base64_encoded",
    [
        ("GET", "/hello/world", None, {}, b"", None, b"", False),
        # (
        #     "POST",
        #     "/",
        #     {"name": ["me"]},
        #     "field1=value1&field2=value2",
        #     False,
        #     b"name=me",
        #     b"field1=value1&field2=value2",
        # ),
        # (
        #     "GET",
        #     "/my/resource",
        #     {"name": ["me", "you"]},
        #     None,
        #     False,
        #     b"name=me&name=you",
        #     None,
        # ),
        # (
        #     "GET",
        #     "",
        #     {"name": ["me", "you"], "pet": ["dog"]},
        #     None,
        #     False,
        #     b"name=me&name=you&pet=dog",
        #     None,
        # ),
        # # A 1x1 red px gif
        # (
        #     "POST",
        #     "/img",
        #     None,
        #     b"R0lGODdhAQABAIABAP8AAAAAACwAAAAAAQABAAACAkQBADs=",
        #     True,
        #     b"",
        #     b"GIF87a\x01\x00\x01\x00\x80\x01\x00\xff\x00\x00\x00\x00\x00,"
        #     b"\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;",
        # ),
        # ("POST", "/form-submit", None, b"say=Hi&to=Mom", False, b"", b"say=Hi&to=Mom"),
    ],
)
def test_aliyun_api_gateway_scope_real(
    method,
    path,
    headers,
    query_parameters,
    expected_query_string,
    path_parameters,
    body,
    body_base64_encoded,
):
    event = get_mock_aliyun_api_gateway_event(
        method,
        path,
        headers,
        query_parameters,
        path_parameters,
        body,
        body_base64_encoded
    )
    example_context = {}
    handler = AliyunApiGateway(event, example_context)

    scope_path = path
    if scope_path == "":
        scope_path = "/"

    assert handler.request.scope == {
        "asgi": {"version": "3.0"},
        "aws.context": {},
        "aws.event": event,
        "aws.eventType": "ALIYUN_API_GATEWAY",
        "client": (None, 0),  # TODO - change after adding support for source ip
        "headers": [],
        "http_version": "1.1",
        "method": method,
        "path": scope_path,
        "query_string": expected_query_string,
        "raw_path": None,
        "root_path": "",
        "scheme": "https",
        # TODO - change after server adding support for CaDomain and CaHttpSchema
        "server": ("mangum", 80),
        "type": "http",
    }

    assert handler.body == b""

# TODO - more tests
# @pytest.mark.parametrize(
#     "method,path,multi_value_query_parameters,req_body,body_base64_encoded,"
#     "query_string,scope_body",
#     [
#         ("GET", "/test/hello", None, None, False, b"", None),
#     ],
# )
# def test_aws_api_gateway_base_path(
#     method,
#     path,
#     multi_value_query_parameters,
#     req_body,
#     body_base64_encoded,
#     query_string,
#     scope_body,
# ):
#     event = get_mock_aws_api_gateway_event(
#         method, path, multi_value_query_parameters, req_body, body_base64_encoded
#     )

#     async def app(scope, receive, send):
#         assert scope["type"] == "http"
#         assert scope["path"] == urllib.parse.unquote(event["path"])
#         await send(
#             {
#                 "type": "http.response.start",
#                 "status": 200,
#                 "headers": [[b"content-type", b"text/plain"]],
#             }
#         )
#         await send({"type": "http.response.body", "body": b"Hello world!"})

#     handler = Mangum(app, lifespan="off", base_path=None)
#     response = handler(event, {})

#     assert response == {
#         "body": "Hello world!",
#         "headers": {"content-type": "text/plain"},
#         "multiValueHeaders": {},
#         "isBase64Encoded": False,
#         "statusCode": 200,
#     }

#     async def app(scope, receive, send):
#         assert scope["type"] == "http"
#         assert scope["path"] == urllib.parse.unquote(
#             event["path"][len(f"/{api_gateway_base_path}") :]
#         )
#         await send(
#             {
#                 "type": "http.response.start",
#                 "status": 200,
#                 "headers": [[b"content-type", b"text/plain"]],
#             }
#         )
#         await send({"type": "http.response.body", "body": b"Hello world!"})

#     api_gateway_base_path = "test"
#     handler = Mangum(app, lifespan="off", base_path=api_gateway_base_path)
#     response = handler(event, {})
#     assert response == {
#         "body": "Hello world!",
#         "headers": {"content-type": "text/plain"},
#         "multiValueHeaders": {},
#         "isBase64Encoded": False,
#         "statusCode": 200,
#     }


# @pytest.mark.parametrize(
#     "method,content_type,raw_res_body,res_body,res_base64_encoded",
#     [
#         ("GET", b"text/plain; charset=utf-8", b"Hello world", "Hello world", False),
#         # A 1x1 red px gif
#         (
#             "POST",
#             b"image/gif",
#             b"GIF87a\x01\x00\x01\x00\x80\x01\x00\xff\x00\x00\x00\x00\x00,"
#             b"\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;",
#             "R0lGODdhAQABAIABAP8AAAAAACwAAAAAAQABAAACAkQBADs=",
#             True,
#         ),
#     ],
# )
# def test_aws_api_gateway_response(
#     method, content_type, raw_res_body, res_body, res_base64_encoded
# ):
#     async def app(scope, receive, send):
#         assert scope["aws.eventType"] == "AWS_API_GATEWAY"
#         await send(
#             {
#                 "type": "http.response.start",
#                 "status": 200,
#                 "headers": [[b"content-type", content_type]],
#             }
#         )
#         await send({"type": "http.response.body", "body": raw_res_body})

#     event = get_mock_aws_api_gateway_event(method, "/test", {}, None, False)

#     handler = Mangum(app, lifespan="off")

#     response = handler(event, {})
#     assert response == {
#         "statusCode": 200,
#         "isBase64Encoded": res_base64_encoded,
#         "headers": {"content-type": content_type.decode()},
#         "multiValueHeaders": {},
#         "body": res_body,
#     }
