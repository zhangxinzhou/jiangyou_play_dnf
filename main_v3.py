import os
import time

import v3_dnf_arbitrator_auto_play

if __name__ == '__main__':
    # 下载redis https://github.com/microsoftarchive/redis/releases
    # 将下载的redis,配置到环境变量
    # 将redis设置为开机启动: win+r -> 输入 shell:startup -> 创建start_redis-server.bat -> bat文件内容:D:; cd  D:\redis_tmp; redis-server
    # 重置redis数据: win+r -> 输入cmd -> 输入redis-cli 回车 进入redis客户端 -> 输入flushdb 回车 清空全部数据

    # 启动 v2_dnf_arbitrator_detection.py
    os.system('cmd /c start "detection_job" python v3_dnf_arbitrator_detection.py')
    # 启动play
    time.sleep(1)
    try:
        v3_dnf_arbitrator_auto_play.play()
    except Exception as e:
        print("system error, exit")
        print(e)
    else:
        print("system run success,exit")
    finally:
        # 最后关机 300秒
        # os.system('shutdown -s -t 300')
        print("finish")


