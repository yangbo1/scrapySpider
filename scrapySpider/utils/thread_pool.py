from concurrent.futures import ThreadPoolExecutor, as_completed

# 最大线程数
MAX_WORKERS = 50


class ThreadPool:
    __instance = None

    def __init__(self):
        self.__executor = ThreadPoolExecutor(MAX_WORKERS)

    def __new__(cls, *args, **kwargs):
        """
        使用单例模式\n
        :param args:
        :param kwargs:
        :return:
        """
        if cls.__instance is None:
            cls.__instance = object.__new__(cls)
        return cls.__instance

    def submit(self, func, *args, **kwargs):
        return self.__executor.submit(func, *args, **kwargs)

    def batch_submit(self, func, *args, **kwargs):
        return [self.submit(func, *item, **kwargs) for item in args]

    @staticmethod
    def completed_tasks(tasks):
        return as_completed(tasks)