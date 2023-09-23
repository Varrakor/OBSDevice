NAME=OBSDevice.app
APP=~/Applications/$NAME

cd ~/Desktop/masters/yr5-sem1/design/project/app
rm -rf dist build $APP
python3 setup.py py2app
cp -r dist/$NAME $APP