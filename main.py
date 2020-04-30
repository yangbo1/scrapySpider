import subprocess
import time

import schedule as schedule
from scrapy.cmdline import execute
execute('scrapy crawl weibo -s LOG_FILE=all.log'.split())
# def task():
#     # 你的spider启动命令
#     execute('scrapy crawl weibo -s LOG_FILE=all.log'.split())
    # subprocess.Popen('scrapy crawl weibo -s LOG_FILE=all.log'.split())
    # pass

# if __name__ == "__main__":
#     task()
#     schedule.every(1).minute.do(task)
#     while True:
#         schedule.run_pending()
#         time.sleep(1)
