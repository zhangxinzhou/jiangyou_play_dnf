import os
import time

import v3_dnf_arbitrator_auto_play

if __name__ == '__main__':
    # 启动docker的redis
    os.system("docker start redis_zxz")
    # 启动 v2_dnf_arbitrator_detection.py
    os.system('cmd /c start "detection_job" python v3_dnf_arbitrator_detection.py')
    # 启动play
    time.sleep(1)
    v3_dnf_arbitrator_auto_play.play()
