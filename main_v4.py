import datetime
import os
import time
import logging

import v4_dnf_arbitrator_auto_play as auto_play

if __name__ == '__main__':
    # 下载redis https://github.com/microsoftarchive/redis/releases
    # 将下载的redis,配置到环境变量
    # 将redis设置为开机启动: win+r -> 输入 shell:startup -> 创建start_redis-server.bat -> bat文件内容:D:; cd  D:\redis_tmp; redis-server
    # 重置redis数据: win+r -> 输入cmd -> 输入redis-cli 回车 进入redis客户端 -> 输入flushdb 回车 清空全部数据

    # 启动 v2_dnf_arbitrator_detection.py
    os.system('cmd /c start "detection_job" python v4_dnf_arbitrator_detection.py')
    # 启动play
    time.sleep(1)
    try:
        auto_play.play()
    except Exception as e:
        print("system error, exit")
        logging.log(e)
    except KeyboardInterrupt as e:
        print("system interrupt, exit")
        logging.log(e)
    else:
        print("system run success,exit")
    finally:
        # 最后关机 300秒AH
        print("finish")
        # 判断是不是工作日，工作日关机
        now = datetime.datetime.now()
        weekday = now.weekday()
        work_day: bool = weekday < 5
        print(f"是否周末：{work_day}")
        shutdown: bool = not auto_play.PROGRAM_EXIT and work_day
        if shutdown:
            print('xxxx')
            os.system('shutdown -s -t 300')

            # stop关机命令
            # os.system('shutdown /a')
