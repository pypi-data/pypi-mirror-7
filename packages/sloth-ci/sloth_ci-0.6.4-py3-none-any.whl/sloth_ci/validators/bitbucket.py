def validate(request, validation_data):
    """Validate Bitbucket payload against repo name (obtained from the Sloth app config).

    :param request_params: payload to validate
    :param validation_data: dictionary with the key ``repo`` (in the form "username/repo")

    :returns: (True, success message, extracted data dict) if the payload is valid, (False, error message, extracted data dict) otherwise
    """

    from json import loads

    if request.method != 'POST':
        return (False, 'Payload validation failed: Wrong method, POST expected, got {method}.', {'method': request.method})

    trusted_ips = ['131.103.20.165', '131.103.20.166']

    remote_ip = request.headers['Remote-Addr']

    if remote_ip not in trusted_ips:
        return (False, 'Payload validation failed: Unverified remote IP: {ip}.', {'ip': remote_ip})

    try:
        payload = request.params.get('payload')

        parsed_payload = loads(payload)

        repo = parsed_payload['repository']['owner'] + '/' + parsed_payload['repository']['slug']
        branch = parsed_payload['commits'][-1]['branch']

        if repo != validation_data['repo']:
            return (False, 'Payload validation failed: repo mismatch. Repo: {repo}', {'repo': repo})

        return (True, 'Payload validated. Branch: {branch}', {'branch': branch})

    except Exception as e:
        return (False, 'Payload validation failed: %s' % e, {})
