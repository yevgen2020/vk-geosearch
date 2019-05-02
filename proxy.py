#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio


from proxybroker import Broker

host, port = '127.0.0.1', 8888
loop = asyncio.get_event_loop()
types = ['HTTPS']
codes = [200, 301, 302]

countries = ['FR', 'DE', 'CA', 'NL', 'US']

broker = Broker(max_tries=1, loop=loop)

broker.serve(host=host, port=port, types=types, limit=10, max_tries=1,
             min_req_proxy=5, max_error_rate=0.5, max_resp_time=8, countries=countries, backlog=100)

loop.run_forever()

