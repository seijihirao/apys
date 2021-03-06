import os
import aiohttp
import json
import random
import contextlib


class CLI:

    def __init__(self, result):
        self.action = 'store_true'
        self.default = False
        self.help = 'Unit test your app'
        self.result = result
        self.config = 'tests'

    async def start(self, api, endpoints):
        """
        Starts testing

        :param api: api object
        :param endpoints: endpoint list
        """
        api.debug('')
        api.debug('{}{}========== Starting tests =========={}'.format(
            api.bcolors.HEADER, api.bcolors.BOLD, api.bcolors.ENDC))

        async with aiohttp.ClientSession() as session:

            test_success = 0
            test_errors = 0

            # Starting tests for each endpoint
            for endpoint in endpoints:
                path = './tests/{}.json'.format(endpoint['url'])
                if os.path.exists(path):
                    api.debug('')
                    api.debug('{}{}--- TEST {} ---{}'.format(
                        api.bcolors.OKBLUE, api.bcolors.BOLD, endpoint['url'], api.bcolors.ENDC))
                    api.debug('')

                    with open(path, 'r') as test_file:
                        tests_json = json.loads(test_file.read())

                        tests = tests_json['tests']
                        for test in tests:

                            # Make request
                            with open(os.devnull, "w") as f, contextlib.redirect_stdout(f):  # disable logs
                                response = await getattr(session, test['method'])(
                                    'http://127.0.0.1:{}/{}'.format(api.config['server']['port'], endpoint['url']),
                                    json=test['input'])

                            # Error expected
                            if 'error' in test:
                                if test['error'] == response.status:
                                    api.debug('{}[OK] {}{}'.format(
                                        api.bcolors.OKGREEN, test['description'], api.bcolors.ENDC))

                                    test_success += 1
                                else:
                                    api.error('[ERROR] {}'.format(test['description']))
                                    api.debug(' > expected status: {}'.format(test['error']))
                                    api.error(' > actual status: {}'.format(response.status))

                                    test_errors += 1

                            # Success expected
                            else:
                                if test['output'] == await response.json():
                                    api.debug('{}[OK] {}{}'.format(
                                        api.bcolors.OKGREEN, test['description'], api.bcolors.ENDC))

                                    test_success += 1
                                else:
                                    api.error('[ERROR] {}'.format(test['description']))
                                    if response.status >= 400:
                                        api.debug(' > expected status: 2XX or 3XX')
                                    api.debug(' > expected response: {}'.format(test['output']))
                                    if response.status >= 400:
                                        api.error(' > actual status: {}'.format(response.status))
                                    api.error(' > actual response: {}'.format(await response.json()))

                                    test_errors += 1

                # Test file not found
                else:
                    api.debug('')
                    api.error('{}--- TEST {} NOT FOUND ---'.format(api.bcolors.BOLD, endpoint['url'], path))

            api.debug('')
        api.debug('{}{}========== Finished tests =========={}'.format(
            api.bcolors.HEADER, api.bcolors.BOLD, api.bcolors.ENDC))
        api.debug('OK: {}'.format(test_success))
        api.debug('ERROR: {}'.format(test_errors))
