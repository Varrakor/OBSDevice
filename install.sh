cd ~/Downloads/OBSDevice/python
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r req_mac.txt
source ./make_app.sh
