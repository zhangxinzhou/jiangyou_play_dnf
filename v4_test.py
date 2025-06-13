import json

import redis

# redis
REDIS_POOL = redis.ConnectionPool(host='localhost', port=6379)
REDIS_CONN = redis.Redis(connection_pool=REDIS_POOL, decode_responses=True)

_last_n_labels = json.loads(REDIS_CONN.get('last_n_labels_detail_dict'))
for _index, _one in enumerate(_last_n_labels):
    _labels_dict: dict = _one
    if _labels_dict is None:
        _labels_dict = {}
    _labels_list = [_key for _key, _val in _labels_dict.items()]

    print(_index, _labels_list, _labels_dict)
