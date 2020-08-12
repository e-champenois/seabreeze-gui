from os import mkdir
from os.path import isdir
from datetime import date

hdd = "/media/xmas/HDD1/"
docs = "/home/xmas/Documents/"
data = hdd + "Data/"
logs = hdd + "Logs/"
python = docs + "Python/"
xmas = python + "xmas/"

def return_folder(folder):
	if not isdir(folder):
		mkdir(folder)
	return folder

def today():
    return return_folder(data + date.today().strftime("%Y%m%d") + "/")

def oceanoptics():
	return return_folder(today() + "oceanoptics/")

def sophia():
	return return_folder(today() + "sophia/")

def sophia_bgs():
	return return_folder(sophia() + "bgs/")

def uldaq():
	return return_folder(today() + "uldaq/")
