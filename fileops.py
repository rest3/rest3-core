from redis import StrictRedis
import os
import logging


logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger()


def get_redis_client():
    return StrictRedis(host=os.environ.get("REDIS_HOST"))


def initialize():
    r = get_redis_client()
    if r.lindex("buckets", 0) is None:
        r.lpush("buckets", "default")


def newbucket(name, metadata=None):
    r = get_redis_client()
    r.hset("buckets", name, '/' + name)
    if metadata is not None:
        addobjectmetadata(name, name, metadata)
    return 'OK'


def getbuckets():
    r = get_redis_client()
    buckets = r.hgetall("buckets")
    bucket_list = []
    for bucket in buckets:
        bucket_obj = {'name': bucket, 'length': r.hlen("bucket_{0}".format(bucket))}
        bucket_list.append(bucket_obj)
    return bucket_list


def getbucketinfo(bucket):
    r = get_redis_client()
    return r.hgetall("bucket_{0}".format(bucket))


def deletebucket(bucket):
    r = get_redis_client()
    r.hdel("buckets", bucket)
    return


# TODO check if bucket already exists. Should bucket be a hashset?
def addobjectmetadata(bucket, obj, metadata):
    r = get_redis_client()
    r.hset("bucket_{0}".format(bucket), obj, metadata)
    return 'OK'


def updateobjectmetadata(bucket, obj, metadata):
    r = get_redis_client()
    r.hset("bucket_{0}".format(bucket), obj, metadata)
    return 'OK'


def removeobjectmetadata(bucket, obj):
    r = get_redis_client()
    r.hdel("bucket_{0}".format(bucket), obj)
    return 'OK'
