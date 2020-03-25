#!/bin/bash 

. ~/.bash_profile

work_dir=`dirname $0`
cd $work_dir/..

# Path to the Azure Usage dump one drive directory managed by Ian by Ian/Warwick
input_dir=~/The\ Alan\ Turing\ Institute/Azure\ Usage\ dump\ -\ Documents/

output_dir=data/

##################################################################################
# Preparing data
##################################################################################

if ! [ -z "$(ls -A "$output_dir")" ]; then
    # backing up old data directory
    tar -zcvf backup_$(date '+%Y-%m-%d-%H-%M-%S').tar.gz "$output_dir"

    # emptying the output direcotory
    rm -rf "$output_dir"*
fi

# Prepares data based on the 
python utils/prep_data.py -i "$input_dir" -o "$output_dir" 

##################################################################################
# Pulling the latest version from git
##################################################################################

git checkout master
git pull

##################################################################################
# Building and pushing container
##################################################################################

echo $DOCKER_PASSWORD | docker login -u $DOCKER_USER --password-stdin

make build

make push

