import json
from typing import Iterable


class Exceptions:
    @staticmethod
    def user_not_found(user_id: int, start_response) -> Iterable[bytes]:
        start_response('404 Not Found', [('Content-Type', 'application/json')])
        return [json.dumps({'message': f'User ({user_id}) not found'}).encode('utf-8')]

    @staticmethod
    def job_not_found(job_id: int, start_response) -> Iterable[bytes]:
        start_response('404 Not Found', [('Content-Type', 'application/json')])
        return [json.dumps({'message': f'Job ({job_id}) not found'}).encode('utf-8')]
