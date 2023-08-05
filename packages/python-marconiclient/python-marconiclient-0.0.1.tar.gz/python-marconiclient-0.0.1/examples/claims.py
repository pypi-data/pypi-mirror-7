# Copyright (c) 2014 Rackspace, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import time

from marconiclient.queues.v1 import client

URL = 'http://localhost:8888'

cli = client.Client(URL)
queue = cli.queue('worker-jobs')


def send_jobs():
    jobs = [
        {'name': 'fluffy'},
        {'name': 'scout'},
        {'name': 'jo'}
    ]
    queue.post([{'body': j,
                 'ttl': 360}
                for j in jobs])


def process_jobs():
    while True:
        claim1 = queue.claim(ttl=500, grace=900, limit=2)
        for msg in claim1:
            claim_id = msg.claim_id
            print('{claim_id} =? {id}'.format(claim_id=claim_id, id=claim1.id))
            print('processing job %s' % (msg))
            msg.delete()
            claim2 = queue.claim(id=claim_id)
            print(claim2)
        print('nothing to do but have a sleep :)')
        time.sleep(1)

if __name__ == '__main__':
    send_jobs()
    process_jobs()
