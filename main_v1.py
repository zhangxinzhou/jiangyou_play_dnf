import os
import v1_dnf_arbitrator_auto_play

if __name__ == '__main__':
    # 启动docker的redis
    os.system("docker start redis_zxz")
    # 启动play
    v1_dnf_arbitrator_auto_play.play()
