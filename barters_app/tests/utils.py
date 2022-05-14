def enrich_request(request, refresh_token, access_token, csrf_token):
    '''Ammend COOKIES, META and header data to the given request'''

    # if refresh_token and csrf_token:
    request.COOKIES.update({
        'refreshtoken': refresh_token,
        'csrftoken': csrf_token
    })
    
    # if csrf_token:
    request.META.update({
        'X-CSRFToken': csrf_token
    })

    # if access_token:
    headers = {
        'Authorization': f'Token {access_token}',
    }

    request.headers = headers

    return request
