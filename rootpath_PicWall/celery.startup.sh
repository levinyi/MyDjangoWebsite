# 后台执行
celery -A rootpath_PicWall worker --loglevel=DEBUG --logfile=./celery.log -D
celery -A rootpath_PicWall worker --loglevel=INFO --logfile=./celery.log -D
nohup celery -A rootpath_PicWall worker --loglevel=DEBUG --logfile=./celery.log -D > nohup.celery.out 2>&1 &
celery -A rootpath_PicWall worker --loglevel=DEBUG --logfile=./celery.log -D > nohup.celery.out 2>&1 &
# 查看是否执行
ps aux |grep 'celery'

# 终止任务
kill <pid>

# Note：前期开发阶段，最好前台使用，随时断开重启，修改了tasks.py之后最好重新启动一下： celery -A mysite worker
