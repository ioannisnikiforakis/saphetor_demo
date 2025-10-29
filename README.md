# saphetor_demo
Assignment for Saphetor

1. Description:

This application implements a simple REST API that will manipulate data imported on an sqlite DB from a VCF file.
To do that it utilises Django/DRF (plus various middleware) and the VCFpy parser library. When a modification is done
to the original data (Adding rows/lines, Editing or deleting them), a Celery task (via Redis) will implement the changes to
the physical file that was copied in the files project folder, by the import script (see below).

2. Installation (linux/mac):
It is suggested that you create a virtual environment to install and test this application in, so i.e.

# Create a new directory to keep everything contained and create/activate your env i.e.
mkdir saphetor_demo
cd saphetor_demo
python3 -m venv saphetor_env
source saphetor_env/bin/activate

# Clone the repo from github and cd in the project folder
git clone git@github.com:ioannisnikiforakis/saphetor_demo.git
cd saphetor_demo/


# Some Prerequisites(Important):
# 1. Install Redis, follow the instructions on https://redis.io/docs/latest/operate/oss_and_stack/install/archive/install-redis/ 
# fitting for your system i.e. on mac you would use Homebrew: "brew install redis"
# 2. If you do not have pip on your system install the appropriate version via: https://pip.pypa.io/en/latest/installation/

# Run the setup script. This will install all the necessary Django/DRF related modules plus Celery and VCFpy
./set_dependencies.sh 

# Run the project tests
# NOTE: You should see "Ran XX tests" and an OK as a result
python3 manage.py test --settings=saph_assignment.test_settings

3. Running the project (linux/mac):

# Insert a VCF file into the project. The file will take a while to import depending on size. 
# On success it should be copied on the files folder where it will be modified henceforth.
# NOTE: The dbupdate.sh script that will perform the insert will also do a first time sqlite db
# setup via Django migrations. You can also rerun it with any valid VCF file you like and it
# will rewrite application data. You need to stop the app first (see below)
# To run the update script from the scripts folder i.e. 
./scripts/dbupdate.sh -f ../NA12877_API_10_2025.vcf 

# After succesfull data insertion the App is ready to use. You can run it via supervisor with the command
# below. This application will run Redis , the Dev Django server on port 8000 and Celery (see vcfApi.conf)
# NOTE: You can stop the app by Control-C or kill it via "kill -15 <pid>" if you run it on the background via & 
supervisord -c vcfapi.conf
Or
supervisord -c vcfapi.conf & 

4. Testing the App/ Examples of Use
You obviously can use Postman or any method you like. The tests below are performed via httpie.
(i.e. python -m pip install httpie)

