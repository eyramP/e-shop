def get_current_host(request):
    """Helper method for getting """
    protocol = request.is_secure() and 'https' or 'http'
    host = request.get_host()
    return "{protocol}://{host}/api/".format(protocol=protocol, host=host)
