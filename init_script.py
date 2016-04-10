__author__ = 'scott'

import os,sys

# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "database.showbox.showbox.settings")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "crawler.settings")
os.environ["DJANGO_SETTINGS_MODULE"] = "crawler.settings"
pwd =''
# os.environ['PYTHONPATH']=os.environ['PYTHONPATH'] + pwd
# print os.environ['PYTHONPATH']
PRJ_PATH = os.path.dirname(os.path.abspath(__file__))

LIBS=(
	PRJ_PATH,
	"%s/crawler"%PRJ_PATH,
)
for lib in LIBS:
	sys.path.insert(0,lib)

# os.environ['SNS_PATH'] = PRJ_PATH



if __name__ == '__main__':
	print os.environ['SNS_PATH']
	print globals()