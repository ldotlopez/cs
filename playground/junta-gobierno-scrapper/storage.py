class ItemType:
    CONTAINER = 0
    ENTRY = 1

ItemInfo = collections.namedtuple('ItemInfo', ['name', 'type'])


class BaseStorage:
    def __init__(*args, **kwargs):
        pass

    def stat(self, name):
        pass

    def open(self, name, mode='rb'):
        pass

    def list(self, container='/'):
        pass


class Storage:
    def load(self, name):
        with self.open(name, 'rb') as fh:
            return fh.read()

    def dump(self, name, data):
        with self.open(name, 'wb') as fh:
            fh.write(data)

    def walk(self, container):
        children = self.list(container):    
        containers = []
        entries = []
        
        for (name, info) in self.list(container):
            if info.type = ItemType.CONTAINER:
                containers.append(name)
            else:
                entries.append(name)

            yield (container, containers, entries)

            for container in containers:
                yield from self.walk(name + '/' + container)
