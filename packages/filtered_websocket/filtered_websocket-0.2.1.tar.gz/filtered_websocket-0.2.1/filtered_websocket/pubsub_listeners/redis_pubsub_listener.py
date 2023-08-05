class RedisPubSubListener(object):

    kill_channel = "__KILL__"

    def __init__(self, redis_client, channels=None):
        self.redis_client = redis_client
        if channels is None:
            channels = ["global"]
        channels += [self.kill_channel]
        self.pubsub = self.redis_client.pubsub()
        self.pubsub.subscribe(channels)
        self.__KILL__ = False

    def kill(self):
        self.__KILL__ = True
        self.redis_client.publish(self.kill_channel, "#YOLO")

    def listener(self, web_socket_instance):
        # Adds data to the web_socket_instance's queue so that
        # a consumer can act on it.
        for data in self.pubsub.listen():
            web_socket_instance.queue.append(data)
            if self.__KILL__ is True:
                self.pubsub.unsubscribe()
                break
