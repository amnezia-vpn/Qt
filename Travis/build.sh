#!/bin/bash
echo "Build script started ..."

# Hold on to current directory
project_dir=$(pwd)
script_dir=${project_dir}/Travis/
third_dir=${project_dir}/../3rd/

unameOut="$(uname -s)"
case "${unameOut}" in
    Linux*)     MACHINE=Linux;;
    Darwin*)    MACHINE=MacOS;;
    CYGWIN*)    MACHINE=Windows;;
    MINGW*)     MACHINE=Windows;;
    *)          MACHINE="UNKNOWN:${unameOut}"
esac

if [ ${MACHINE} = "MacOS" ]; then
   echo 'export PATH="/usr/local/opt/mysql-client/bin:$PATH"' >> ~/.bash_profile
   echo 'export PATH="/usr/local/opt/qt/bin:$PATH"' >> ~/.bash_profile
   source ~/.bash_profile
fi

# should be after source ~/.bash_profile
set -e -o nounset

echo "Project dir: ${project_dir}"
echo "3rd Party dir: ${third_dir}"

TRAVIS_TAG=${TRAVIS_TAG:-$(date +'%Y.%m.%d_%H.%M.%S')-$(git log --format=%h -1)}
APP_FILE_NAME=Qt_${TRAVIS_TAG}_${MACHINE}

echo "Building for branch ${TRAVIS_BRANCH}"
echo "Building TAG ${TRAVIS_TAG}"

ZIP_FILE_NAME=${APP_FILE_NAME}.tar.gz

echo "Target file is ${ZIP_FILE_NAME}"

# Build App
# Due 120 minutes limit build either 3rd party as first step or project as second step
# When 3rd party build completed it will be cached by travis

TS_3RD_START=$(date +%s)
echo "Build 3rd party started at ${TS_3RD_START}"

python3 build_qt.py 5.12 5| cut -c1-100

TS_3RD_FINISH=$(date +%s)
echo "Build 3rd party finished at ${TS_3RD_FINISH}"

# 45 min
if [ $((${TS_3RD_FINISH} - ${TS_3RD_START})) -gt "3150" ]; then
    echo "Build 3rd party took more than one hour, exitting"
    exit 0
fi


#echo "Deploy..."

# Package 
#echo "Packaging ..."
#ls -al ${build_dir}
#tar -czvf  ${script_dir}/${ZIP_FILE_NAME} ${build_dir}
#echo "Deploy is done"

# _________________________________________________________________
#echo "Deploy to Releases"
#chmod +x ${script_dir}/push_github.sh

# $GH_API_TOKEN comes from travis.yml env  

#GH_TAG=${TRAVIS_TAG}
#${script_dir}/push_github.sh github_api_token=$GH_API_TOKEN owner_repo=$TRAVIS_REPO_SLUG tag=$GH_TAG filename=${script_dir}/${ZIP_FILE_NAME}


exit 0
