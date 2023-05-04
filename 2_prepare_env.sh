export $(cat .env | xargs)

# install dependencies
sudo apt-get install python3-venv
python3 -m venv spotify_project_venv
source spotify_project_venv/bin/activate
pip install -r requirements.txt