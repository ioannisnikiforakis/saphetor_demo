#!/bin/bash

echo "Migrating latest changes..."
python3 manage.py migrate

copy_set_source() {
  filetocheck="$1"
  if [ -f "$filetocheck" ] ; then
	echo "$filetocheck exists. Copying to the files folder and setting as source for the insert script..."
	basename=$(basename "$filetocheck")
	cp "$filetocheck" files/"$basename"
	export VCF_FILE_SOURCE=files/"$basename"
	export VCF_FILE_NAME="$basename"
	echo "Inserting file to Db. Please wait..."
	python3 manage.py update_db --settings=saph_assignment.proc_settings
	echo File Insertion Process Completed. Please run the application via "supervisord -c vcfapi.conf" to confirm data installation.
  else
        echo "file $filetocheck could not be found! Did you enter the full correct path?"
  fi
}

case $1 in 
     -f)
       copy_set_source $2   
     ;;
esac
