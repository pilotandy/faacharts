Maptiles
FAA VFR and IFR chart download, transform, tile and publish to website.


Prereqs:
sudo apt install git gdal-bin libgdal-dev python3.9-dev python3.9-venv


Define environment variables:
WEB_HOST        Website backend
WEB_USER        Username to talk to website
WEB_PASS        Password
JWT_SECRET_KEY  JWT key to talk to website
WORK_ROOT       Root path to download zips and process
