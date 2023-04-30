# celery -A rootpath_PicWall worker --loglevel=info  --logfile=./celery.log  -D
celery -A rootpath_PicWall worker --loglevel=DEBUG --logfile=./celery.log  -D

# ps aux | grep 'celery'
# kill <pid>

