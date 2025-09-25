

def output_request_info(request):
    print("--- Request Details ---")
    print(f"Method: {request.method}")
    print(f"URL: {request.url}")
    print(f"Headers: {request.headers}")
    print(f"Arguments (query parameters): {request.args}")
    print(f"Form data: {request.form}")
    print(f"JSON data: {request.json}")
    print(f"Cookies: {request.cookies}")
    print(f"Remote Address: {request.remote_addr}")
    print("-----------------------")
    return "Check your server console for request details."