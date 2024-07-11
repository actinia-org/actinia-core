<!-- markdownlint-configure-file { "MD013": { "line_length": 1150 } } -->
# Actinia supports logging to fluentd as well as to stdout

## tl;dr

- Rename logfile in actinia.cfg in project setups from
  `worker_logfile = /actinia_core/workspace/tmp/actinia_worker` to
  `worker_logfile = /actinia_core/workspace/tmp/actinia_worker.log`. If you leave it,
  it won't break something but would be nice for consistency.
- Adjust logging config as wished (fluentd/stdout with json/stdout colored).
  If your setup includes Kibana, `log_stdout_format = json` is recommended while
  `log_stdout_format = colored` provides better human readability. More infos below.

## Standard Output Logging Infos

### Configuration

Example:

```ini
[LOGGING]
log_interface = stdout
log_stdout_format = colored
log_file_format = colored
log_stderr_format = plain
log_level = 4
```

The `log_interface`s `fluentd` and `stdout` are mutually exclusive, while actinia
will always log to a file. If `log_interface = stdout`, it can be chosen between
`json` output (e.g. for kibana) and `colored` for human readability.
The `log_file_format` has the same options and is independent. The option
`log_stderr_format` is useful for debugging and won't appear in fluentd. In
case this is a stacktrace, it is logged line by line, each wrapped by the log
formatter (either json or stdout, depending on which one is set). As it is
hardly readable and context can get lost, only use with `json` when needed
by e.g. kibana, else use option `plain` for a readable stacktrace. It will also
log to file with configured formatter and log level `CRITICAL`.

For more information, see
https://github.com/actinia-org/actinia-core/blob/main/src/actinia_core/resources/common/config.py#L132.

### Dev / Debug Hints

- one disadvantage of general actinia logging implementation is, that log messages
  are passed to `redis_fluentd_logger_base` where they are initially logged.
  This way, it always logs as source
  `/usr/lib/python3.8/site-packages/actinia_core-0.99.5.post0.dev18+g4d82691.dirty-py3.8.egg/actinia_core/resources/common/redis_fluentd_logger_base.py:104`
  instead of where the message was generated. To change this, refactoring would be necessary.

### Examples

__Simple log__

```json
{
  "time": "2020-05-06T09:07:33.431255Z",
  "level": "INFO",
  "component": "actinia-core",
  "module": "endpoints",
  "message": "Loading plugin actinia_statistic_plugin",
  "pathname": "/usr/lib/python3.8/site-packages/actinia_core-0.99.5.post0.dev18+g4d82691.dirty-py3.8.egg/actinia_core/endpoints.py",
  "lineno": 172,
  "processName": "MainProcess",
  "threadName": "MainThread",
  "node": "dc05d9be5c7d"
}
```

```text
[2020-05-08 09:19:33,909] INFO      : actinia-core.endpoints  -Loading plugin actinia_statistic_plugin [in /usr/lib/python3.8/site-packages/actinia_core-0.99.5.post0.dev20+gacc075c-py3.8.egg/actinia_core/endpoints.py:172]
```

```json
{
  "time": "2020-05-06T09:07:34.874243Z",
  "level": "INFO",
  "component": "actinia-core",
  "module": "process_queue",
  "message": "Run process: {endpoint: asyncephemeralexportresource, method: POST, path: /api/v3/locations/latlong_wgs84/processing_async_export, request_url: http://127.0.0.1:8088/api/v3/locations/latlong_wgs84/processing_async_export}",
  "pathname": "/usr/lib/python3.8/site-packages/actinia_core-0.99.5.post0.dev18+g4d82691.dirty-py3.8.egg/actinia_core/resources/common/process_queue.py",
  "lineno": 355,
  "processName": "Process-1",
  "threadName": "MainThread"
}
```

```text
[2020-05-08 09:19:48,430] INFO      : actinia-core.process_queue -Run process: {'endpoint': 'asyncephemeralexportresource', 'method': 'POST', 'path': '/api/v3/locations/latlong_wgs84/processing_async_export', 'request_url': 'http://127.0.0.1:8088/api/v3/locations/latlong_wgs84/processing_async_export'} [in /usr/lib/python3.8/site-packages/actinia_core-0.99.5.post0.dev20+gacc075c-py3.8.egg/actinia_core/resources/common/process_queue.py:355]
```

__Gunicorn log__

```json
{
  "time": "2020-05-06T09:07:34.837921Z",
  "level": "INFO",
  "component": "gunicorn.access",
  "module": "glogging",
  "message": "172.20.0.1 - actinia-gdi [06/May/2020:09:07:34 +0000] \"POST /api/v3/locations/latlong_wgs84/processing_async_export HTTP/1.1\" 200 756 \"-\" \"curl/7.58.0\"",
  "pathname": "/usr/lib/python3.8/site-packages/gunicorn/glogging.py",
  "lineno": 344,
  "processName": "MainProcess",
  "threadName": "ThreadPoolExecutor-0_0"
}
```

```text
[2020-05-08 09:19:48,426] INFO      : gunicorn.access.glogging   -172.20.0.1 - actinia-gdi [08/May/2020:09:19:48 +0000] "POST /api/v3/locations/latlong_wgs84/processing_async_export HTTP/1.1" 200 755 "-" "curl/7.58.0" [in /usr/lib/python3.8/site-packages/gunicorn/glogging.py:344]
```

__messages_logger INFO__

```json
{
  "time": "2020-05-06T09:07:34.891945Z",
  "level": "INFO",
  "component": "actinia-core",
  "module": "redis_fluentd_logger_base",
  "message": "{id: v_what_vect_1, module: v.what.vect, inputs: [{param: map, value: point}, {param: column, value: isIn}, {param: query_map, value: polygon}, {param: query_column, value: polygon}]}",
  "pathname": "/usr/lib/python3.8/site-packages/actinia_core-0.99.5.post0.dev18+g4d82691.dirty-py3.8.egg/actinia_core/resources/common/redis_fluentd_logger_base.py",
  "lineno": 109,
  "processName": "Process-1:1",
  "threadName": "MainThread",
  "node": "dc05d9be5c7d",
  "ctime": "Wed May  6 09:07:34 2020",
  "user_id": "actinia-gdi",
  "log_level": "INFO",
  "status": "message",
  "logger": "messages_logger"
}
```

```text
[2020-05-08 09:19:48,512] INFO      : actinia-core.redis_fluentd_logger_base -{'node': '3f3e57b7ab83', 'ctime': 'Fri May  8 09:19:48 2020', 'user_id': 'actinia-gdi', 'log_level': 'INFO', 'status': 'message', 'message': "{'id': 'v_what_vect_1', 'module': 'v.what.vect', 'inputs': [{'param': 'map', 'value': 'point'}, {'param': 'column', 'value': 'isIn'}, {'param': 'query_map', 'value': 'polygon'}, {'param': 'query_column', 'value': 'polygon'}]}", 'logger': 'messages_logger'} [in /usr/lib/python3.8/site-packages/actinia_core-0.99.5.post0.dev20+gacc075c-py3.8.egg/actinia_core/resources/common/redis_fluentd_logger_base.py:99]
```

__api_logger__

```json
{
  "time": "2020-05-06T09:07:34.829927Z",
  "level": "INFO",
  "component": "actinia-core",
  "module": "redis_fluentd_logger_base",
  "message": null,
  "pathname": "/usr/lib/python3.8/site-packages/actinia_core-0.99.5.post0.dev18+g4d82691.dirty-py3.8.egg/actinia_core/resources/common/redis_fluentd_logger_base.py",
  "lineno": 98,
  "processName": "MainProcess",
  "threadName": "ThreadPoolExecutor-0_0",
  "time_stamp": "2020-05-06 09:07:34.826617",
  "node": "dc05d9be5c7d",
  "api_info": {
    "endpoint": "asyncephemeralexportresource",
    "method": "POST",
    "path": "/api/v3/locations/latlong_wgs84/processing_async_export",
    "request_url": "http://127.0.0.1:8088/api/v3/locations/latlong_wgs84/processing_async_export"
  },
  "request_str": "<Request http://127.0.0.1:8088/api/v3/locations/latlong_wgs84/processing_async_export [POST]>",
  "user_id": "actinia-gdi",
  "status": "api_call",
  "logger": "api_logger"
}
```

```text
[2020-05-08 09:19:48,419] INFO      : actinia-core.redis_fluentd_logger_base -{'time_stamp': '2020-05-08 09:19:48.419294', 'node': '3f3e57b7ab83', 'api_info': {'endpoint': 'asyncephemeralexportresource', 'method': 'POST', 'path': '/api/v3/locations/latlong_wgs84/processing_async_export', 'request_url': 'http://127.0.0.1:8088/api/v3/locations/latlong_wgs84/processing_async_export'}, 'request_str': "<Request 'http://127.0.0.1:8088/api/v3/locations/latlong_wgs84/processing_async_export' [POST]>", 'user_id': 'actinia-gdi', 'status': 'api_call', 'logger': 'api_logger'} [in /usr/lib/python3.8/site-packages/actinia_core-0.99.5.post0.dev20+gacc075c-py3.8.egg/actinia_core/resources/common/redis_fluentd_logger_base.py:94]
```

__resources_logger "accepted"__

```json
{
  "time": "2020-05-06T09:07:34.835133Z",
  "level": "INFO",
  "component": "actinia-core",
  "module": "redis_fluentd_logger_base",
  "message": "Resource accepted",
  "pathname": "/usr/lib/python3.8/site-packages/actinia_core-0.99.5.post0.dev18+g4d82691.dirty-py3.8.egg/actinia_core/resources/common/redis_fluentd_logger_base.py",
  "lineno": 94,
  "processName": "MainProcess",
  "threadName": "ThreadPoolExecutor-0_0",
  "status": "accepted",
  "user_id": "actinia-gdi",
  "resource_id": "resource_id-8fb3b80c-59f8-45e6-b003-04dd83af3d9d",
  "accept_timestamp": 1588756054.8311443,
  "accept_datetime": "2020-05-06 09:07:34.831148",
  "timestamp": 1588756054.8341658,
  "datetime": "2020-05-06 09:07:34.834168",
  "time_delta": 0.003036975860595703,
  "process_results": {},
  "process_chain_list": [],
  "http_code": 200,
  "urls": {
    "resources": [],
    "status": "http://127.0.0.1:8088/api/v3/resources/actinia-gdi/resource_id-8fb3b80c-59f8-45e6-b003-04dd83af3d9d"
  },
  "api_info": {
    "endpoint": "asyncephemeralexportresource",
    "method": "POST",
    "path": "/api/v3/locations/latlong_wgs84/processing_async_export",
    "request_url": "http://127.0.0.1:8088/api/v3/locations/latlong_wgs84/processing_async_export"
  },
  "logger": "resources_logger"
}
```

```text
[2020-05-08 09:19:48,424] INFO      : actinia-core.redis_fluentd_logger_base -{'status': 'accepted', 'user_id': 'actinia-gdi', 'resource_id': 'resource_id-53e2a5ae-d4c0-4b9d-8d24-03030a4b314a', 'accept_timestamp': 1588929588.421158, 'accept_datetime': '2020-05-08 09:19:48.421166', 'timestamp': 1588929588.4238856, 'datetime': '2020-05-08 09:19:48.423887', 'message': 'Resource accepted', 'time_delta': 0.002741098403930664, 'process_results': {}, 'process_chain_list': [], 'http_code': 200, 'urls': {'resources': [], 'status': 'http://127.0.0.1:8088/api/v3/resources/actinia-gdi/resource_id-53e2a5ae-d4c0-4b9d-8d24-03030a4b314a'}, 'api_info': {'endpoint': 'asyncephemeralexportresource', 'method': 'POST', 'path': '/api/v3/locations/latlong_wgs84/processing_async_export', 'request_url': 'http://127.0.0.1:8088/api/v3/locations/latlong_wgs84/processing_async_export'}, 'logger': 'resources_logger'} [in /usr/lib/python3.8/site-packages/actinia_core-0.99.5.post0.dev20+gacc075c-py3.8.egg/actinia_core/resources/common/redis_fluentd_logger_base.py:91]
```

__resources_logger "running"__

```json
{
  "time": "2020-05-06T09:07:35.188501Z",
  "level": "INFO",
  "component": "actinia-core",
  "module": "redis_fluentd_logger_base",
  "message": "Checking access to URL: https://raw.githubusercontent.com/mmacata/pagestest/gh-pages/pointInBonn.geojson",
  "pathname": "/usr/lib/python3.8/site-packages/actinia_core-0.99.5.post0.dev18+g4d82691.dirty-py3.8.egg/actinia_core/resources/common/redis_fluentd_logger_base.py",
  "lineno": 94,
  "processName": "Process-1:1",
  "threadName": "MainThread",
  "status": "running",
  "user_id": "actinia-gdi",
  "resource_id": "resource_id-8fb3b80c-59f8-45e6-b003-04dd83af3d9d",
  "accept_timestamp": 1588756054.8311443,
  "accept_datetime": "2020-05-06 09:07:34.831148",
  "timestamp": 1588756055.187592,
  "datetime": "2020-05-06 09:07:35.187593",
  "time_delta": 0.3564629554748535,
  "progress": {
    "step": 0,
    "num_of_steps": 0
  },
  "process_chain_list": [],
  "http_code": 200,
  "urls": {
    "resources": [],
    "status": "http://127.0.0.1:8088/api/v3/resources/actinia-gdi/resource_id-8fb3b80c-59f8-45e6-b003-04dd83af3d9d"
  },
  "api_info": {
    "endpoint": "asyncephemeralexportresource",
    "method": "POST",
    "path": "/api/v3/locations/latlong_wgs84/processing_async_export",
    "request_url": "http://127.0.0.1:8088/api/v3/locations/latlong_wgs84/processing_async_export"
  },
  "logger": "resources_logger"
}
```

```text
[2020-05-08 09:19:48,514] INFO      : actinia-core.redis_fluentd_logger_base -{'status': 'running', 'user_id': 'actinia-gdi', 'resource_id': 'resource_id-53e2a5ae-d4c0-4b9d-8d24-03030a4b314a', 'accept_timestamp': 1588929588.421158, 'accept_datetime': '2020-05-08 09:19:48.421166', 'timestamp': 1588929588.5140734, 'datetime': '2020-05-08 09:19:48.514093', 'message': 'Checking access to URL: https://raw.githubusercontent.com/mmacata/pagestest/gh-pages/bonn.geojson', 'time_delta': 0.09295296669006348, 'progress': {'step': 0, 'num_of_steps': 0}, 'process_chain_list': [], 'http_code': 200, 'urls': {'resources': [], 'status': 'http://127.0.0.1:8088/api/v3/resources/actinia-gdi/resource_id-53e2a5ae-d4c0-4b9d-8d24-03030a4b314a'}, 'api_info': {'endpoint': 'asyncephemeralexportresource', 'method': 'POST', 'path': '/api/v3/locations/latlong_wgs84/processing_async_export', 'request_url': 'http://127.0.0.1:8088/api/v3/locations/latlong_wgs84/processing_async_export'}, 'logger': 'resources_logger'} [in /usr/lib/python3.8/site-packages/actinia_core-0.99.5.post0.dev20+gacc075c-py3.8.egg/actinia_core/resources/common/redis_fluentd_logger_base.py:91]
```

__resources_logger "error" shortened__

```json
{
  "time": "2020-05-06T09:07:38.357543Z",
  "level": "ERROR",
  "component": "actinia-core",
  "module": "redis_fluentd_logger_base",
  "message": "[Errno 2] No such file or directory: /usr/bin/zip",
  "pathname": "/usr/lib/python3.8/site-packages/actinia_core-0.99.5.post0.dev18+g4d82691.dirty-py3.8.egg/actinia_core/resources/common/redis_fluentd_logger_base.py",
  "lineno": 90,
  "processName": "Process-1:1",
  "threadName": "MainThread",
  "status": "error",
  "user_id": "actinia-gdi",
  "resource_id": "resource_id-8fb3b80c-59f8-45e6-b003-04dd83af3d9d",
  "accept_timestamp": 1588756054.8311443,
  "accept_datetime": "2020-05-06 09:07:34.831148",
  "timestamp": 1588756058.3555682,
  "datetime": "2020-05-06 09:07:38.355575",
  "time_delta": 3.5244598388671875,
  "process_log": [
    {
      "executable": ...,
    },
    ...
  ],
  "progress": {
    "step": 13,
    "num_of_steps": 13
  },
  "process_chain_list": [
    {
      "list": [
        {
          "module": ...
          ...
        },
        ...
      ],
      "version": "1"
    }
  ],
  "http_code": 400,
  "exception": {
    "message": "[Errno 2] No such file or directory: /usr/bin/zip",
    "traceback": [
      "  File \"/usr/lib/python3.8/site-packages/actinia_core-0.99.5.post0.dev18+g4d82691.dirty-py3.8.egg/actinia_core/resources/ephemeral_processing.py\", line 1350, in run\n    self._execute()\n",
     ...
      "  File \"/usr/lib/python3.8/subprocess.py\", line 1702, in _execute_child\n    raise child_exception_type(errno_num, err_msg, err_filename)\n"
    ],
    "type": "<class FileNotFoundError>"
  },
  "urls": {
    "resources": [],
    "status": "http://127.0.0.1:8088/api/v3/resources/actinia-gdi/resource_id-8fb3b80c-59f8-45e6-b003-04dd83af3d9d"
  },
  "api_info": {
    "endpoint": "asyncephemeralexportresource",
    "method": "POST",
    "path": "/api/v3/locations/latlong_wgs84/processing_async_export",
    "request_url": "http://127.0.0.1:8088/api/v3/locations/latlong_wgs84/processing_async_export"
  },
  "logger": "resources_logger"
}
```

```text
[2020-05-08 09:19:54,787] ERROR     : actinia-core.redis_fluentd_logger_base -{'status': 'error', 'user_id': 'actinia-gdi', 'resource_id': 'resource_id-53e2a5ae-d4c0-4b9d-8d24-03030a4b314a', 'accept_timestamp': 1588929588.421158, 'accept_datetime': '2020-05-08 09:19:48.421166', 'timestamp': 1588929594.7862213, 'datetime': '2020-05-08 09:19:54.786227', 'message': "[Errno 2] No such file or directory: '/usr/bin/zip'", ..., 'logger': 'resources_logger'} [in /usr/lib/python3.8/site-packages/actinia_core-0.99.5.post0.dev20+gacc075c-py3.8.egg/actinia_core/resources/common/redis_fluentd_logger_base.py:87]
```

__stderr_logger one random line of stacktrace__

```json
{
  "time": "2020-05-06T13:25:01.369275Z",
  "level": "CRITICAL",
  "component": "actinia-core-stderr",
  "module": "logging_interface",
  "message": "chunk = read(handle, remaining)",
  "pathname": "/usr/lib/python3.8/site-packages/actinia_core-0.99.5.post0.dev18+g4d82691.dirty-py3.8.egg/actinia_core/resources/common/logging_interface.py",
  "lineno": 138,
  "processName": "Process-1",
  "threadName": "Thread-1",
  "node": "dc05d9be5c7d"
}
```

```text
Exception in thread
Thread-1
:
Traceback (most recent call last):
  File "/usr/lib/python3.8/threading.py", line 932, in _bootstrap_inner
self.run()
  File "/usr/lib/python3.8/threading.py", line 870, in run
self._target(*self._args, **self._kwargs)
  File "/usr/lib/python3.8/site-packages/actinia_core-0.99.5.post0.dev20+gacc075c-py3.8.egg/actinia_core/resources/common/process_queue.py", line 262, in queue_watcher
data = queue.get(block=True)
  File "/usr/lib/python3.8/multiprocessing/queues.py", line 97, in get
res = self._recv_bytes()
  File "/usr/lib/python3.8/multiprocessing/connection.py", line 216, in recv_bytes
buf = self._recv_bytes(maxlength)
  File "/usr/lib/python3.8/multiprocessing/connection.py", line 421, in _recv_bytes
return self._recv(size)
  File "/usr/lib/python3.8/multiprocessing/connection.py", line 379, in _recv
chunk = read(handle, remaining)
TypeError
:
an integer is required (got type NoneType)
```

## Fluentd Logging Infos

- Configure in actinia.cfg the connection to fluentd
- Have an elasticsearch and kibana instance ready
- Start all components and set kibana to look at fluentd-\* pattern
