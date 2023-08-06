def singleton(cls):

    def getinstance():
        if cls not in singleton.instances:
            singleton.instances[cls] = cls()
        return singleton.instances[cls]
    return getinstance


singleton.instances = {}
