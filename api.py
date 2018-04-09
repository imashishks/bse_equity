


import redis
import cherrypy
REDIS_HOST = 'localhost'
conn = redis.Redis(REDIS_HOST)
x= conn.scan(0,None,10)
# print(x[1])

for x in x[1]:
    print("ssss",x)