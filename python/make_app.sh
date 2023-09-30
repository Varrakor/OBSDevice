NAME=OBSDevice.app
APP=~/Applications/$NAME
rm -rf dist build $APP
python3 setup.py py2app
cp -r dist/$NAME $APP