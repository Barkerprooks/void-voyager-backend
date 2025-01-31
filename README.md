# Simple Temporary POC for Void Voyager

Just bored at work let me know if this is something you'd be interested in exploring

## How to set up

Quick guide on how to get this project up and running if you're not familiar.

### Clone
```
git clone git@github.com:barkerprooks/void-voyager-backend.git
```

### Set up python environment
```
cd ./void-voyager-backend
python -m venv env
source ./env/bin/activate
pip install -r requirements.txt
```

### Set up the database
```
flask create-database
```

## How to run

After running the above commands the project is now set up. In the future, to run the
project you only need to run this command

### Run the webserver
```
flask run
```