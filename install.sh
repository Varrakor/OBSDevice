cd ./python
rm -rf ./venv
python3 -m venv venv
source ./venv/bin/activate
pip install -r ./req_mac.txt

NAME=OBSDevice.app
APP=~/Applications/$NAME

rm -rf dist build $APP
python3 setup.py py2app
cp -r dist/$NAME $APP

cd ..