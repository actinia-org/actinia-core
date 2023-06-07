# Redis Queue for Jobs

## Dev setup
- adjust config, e.g.
```
[QUEUE]
redis_queue_server_url = redis-queue
redis_queue_server_password = pass
worker_prefix = job_queue
queue_type = per_job
```
or
```
[QUEUE]
number_of_workers = 1
queue_type = redis
```

- Startup actinia with above config in preferred way, e.g.
`cd ~/repos/actinia` + press F5
- Start Container for worker
```
MY_ACTINIA_DATA=$HOME/actinia
docker run --rm -it --entrypoint sh \
    -v $HOME/repos/actinia/actinia-docker/actinia-dev/actinia.cfg:/etc/default/actinia \
    -v $MY_ACTINIA_DATA/workspace:/actinia_core/workspace \
    -v $MY_ACTINIA_DATA/resources:/actinia_core/resources \
    -v $MY_ACTINIA_DATA/grassdb:/actinia_core/grassdb \
    -v $MY_ACTINIA_DATA/grassdb_user:/actinia_core/userdata \
    --network actinia-docker_actinia-dev mundialis/actinia:2.5.6
```
- inside container, start worker listening to specified queue
```
QUEUE_NAME=job_queue_0
rq_custom_worker $QUEUE_NAME -c /etc/default/actinia --quit
```


## Redis Details

```
redis-cli -a 'pass'

127.0.0.1:6379> KEYS *
3) "actinia_worker_count"
9) "rq:workers"
7) "rq:workers:job_queue_0"
4) "rq:worker:04e384aad9e743ffb2fb021cfaad421a"
9) "rq:job:b6de9170-0fa6-4118-8eb7-9d5f43a37c23"
1) "rq:queues"
5) "rq:queue:job_queue_0"
6) "rq:clean_registries:job_queue_0"
5) "rq:failed:job_queue_0"
1) "rq:finished:job_queue_0"
```
### actinia_worker_count
- only in redis_interface for current queue
- created at first HTTP POST request
- currently outcommented

### workers
- exists if at least one worker is active, else deleted.
```r
127.0.0.1:6379> TYPE rq:workers
set
127.0.0.1:6379> SMEMBERS rq:workers
1) "rq:worker:afb2961308964653abd2328893a1cd95"

127.0.0.1:6379> TYPE rq:workers:job_queue_0
set
127.0.0.1:6379> SMEMBERS rq:workers:job_queue_0
1) "rq:worker:afb2961308964653abd2328893a1cd95"

127.0.0.1:6379> TYPE rq:worker:afb2961308964653abd2328893a1cd95
hash
127.0.0.1:6379> HGETALL rq:worker:afb2961308964653abd2328893a1cd95
 1) "birth"
 2) "2022-01-21T13:05:32.355053Z"
 3) "last_heartbeat"
 4) "2022-01-21T13:06:04.545367Z"
 5) "queues"
 6) "job_queue_0"
 7) "pid"
 8) "162"
 9) "hostname"
10) "4c897b45a129"
11) "version"
12) "1.7.0"
13) "python_version"
14) "3.8.5 (default, Jul 20 2020, 23:11:29) \n[GCC 9.3.0]"
15) "state"
16) "idle"
17) "successful_job_count"
18) "1"
19) "total_working_time"
20) "6.920567"
...
15) "state"
16) "busy"
17) "current_job"
18) "626832ff-7998-4276-b0d9-e4fa98b6a69d"
```

### job
- created on job start. Then job is "accepted"
- also for synchronous requests, e.g. GET mapsets, tpl processing, ...
- deleted after a while - TODO check when?
```r
127.0.0.1:6379> TYPE rq:job:b6de9170-0fa6-4118-8eb7-9d5f43a37c23
hash
127.0.0.1:6379> HGETALL rq:job:b6de9170-0fa6-4118-8eb7-9d5f43a37c23
 1) "status"
 2) "finished"
 3) "created_at"
 4) "2022-01-21T13:36:21.700405Z"
 5) "enqueued_at"
 6) "2022-01-21T13:36:21.700609Z"
 7) "data"
 8) "x\x9c\xed\x1a\xcbn\x1c\xc7\x91\xb2\xf9\x14\x1f\x1c......."
 9) "description"
10) "actinia_core.rest.ephemeral_processing_with_export.start_job(<actinia_core.core.resource_data_container.ResourceDataContainer object at ...)"
11) "timeout"
12) "180"
13) "last_heartbeat"
14) "2022-01-21T13:37:39.900333Z"
15) "worker_name"
16) ""
17) "ended_at"
18) "2022-01-21T13:37:48.727823Z"
19) "started_at"
20) "2022-01-21T13:37:40.929638Z"
21) "origin"
22) "job_queue_0"
```

### queues
- rq:queue:job_queue_0 only exists if job in queue
- as soon as worker takes job, queue is removed
- => if no job is left in queue, it is removed
```r
127.0.0.1:6379> TYPE rq:queues
set
127.0.0.1:6379> SMEMBERS rq:queues
1) "rq:queue:job_queue_0"

127.0.0.1:6379> TYPE rq:queue:job_queue_0
list
127.0.0.1:6379> LRANGE rq:queue:job_queue_0 0 -1
1) "b6d8672b-2afc-4740-80d1-46345a28abdf"

127.0.0.1:6379> TYPE rq:failed:job_queue_0
zset
127.0.0.1:6379> ZRANGE rq:failed:job_queue_0 0 -1 WITHSCORES
1) "8b8d4e6a-34ef-4da2-9f86-70b1034664ab"
2) "1674302827"
3) "e27045ef-bdf4-440c-a808-d4e748dfab2f"
4) "1674302827"
5) "dfa4d4fa-39bf-4021-94af-f3d1763dc789"
6) "1674302869"

127.0.0.1:6379> ZRANGE rq:finished:job_queue_0 0 -1 WITHSCORES
1) "b6de9170-0fa6-4118-8eb7-9d5f43a37c23"
2) "1642772768"

```

### misc
```r
127.0.0.1:6379> TYPE rq:clean_registries:job_queue_0
string
127.0.0.1:6379> GET rq:clean_registries:job_queue_0
"1"
```

## Example how to set timeout
```
# requesting jobs in queue (queue name: job_queue_resource_id-665c5ecb-b7b1-4613-9189-2274f0e01cd7)
LRANGE rq:queue:job_queue_resource_id-665c5ecb-b7b1-4613-9189-2274f0e01cd7 0 -1
# requesting job (4b10b746-7842-4bc4-a035-ad908572b1fa)
HGETALL rq:job:4b10b746-7842-4bc4-a035-ad908572b1fa
# set timeout for job to 7200 sec
HSET rq:job:4b10b746-7842-4bc4-a035-ad908572b1fa timeout 7200
# requesting job
HGETALL rq:job:4b10b746-7842-4bc4-a035-ad908572b1fa
```
