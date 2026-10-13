#!/bin/bash
set -e

PROJECT_REPO="https://github.com/Mars-Morth/poke"
PROJECT_DIR="${HOME}/opt/poke/"

# clone clean project
yes | rm -r ${PROJECT_DIR} || true
mkdir -p ${PROJECT_DIR}

if [[ $1 -eq "local" ]]; then
	echo "Getting local project"
	cp -a . ${PROJECT_DIR}
	cd ${PROJECT_DIR}
else
	cd ${PROJECT_DIR}
	git clone --depth=1 ${PROJECT_REPO} .
fi

echo "*********************************************************************"
echo "*********************************************************************"
echo "*********************************************************************"
echo "Finished installing poke"
echo "*********************************************************************"
echo "*********************************************************************"
echo "*********************************************************************"

# daemon and cli install
cd client
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

echo "*********************************************************************"
echo "*********************************************************************"
echo "*********************************************************************"
echo "Finished installing dependancies"
echo "*********************************************************************"
echo "*********************************************************************"
echo "*********************************************************************"

# systemd stuff
cd ${PROJECT_DIR}
mkdir -p ${HOME}/.config/systemd/user
cp ./client/poke.service ~/.config/systemd/user/poke.service
systemctl --user daemon-reload
systemctl --user enable --now poke.service  # NOTE: enable to be on start
systemctl --user status poke.service

echo "*********************************************************************"
echo "*********************************************************************"
echo "*********************************************************************"
echo "Systemd daemon running"
echo "*********************************************************************"
echo "*********************************************************************"
echo "*********************************************************************"

curl -fsSL https://tailscale.com/install.sh | sh

echo "*********************************************************************"
echo "use pokepeoplegd@gmail.com as your tailscale account, check teams for credentials"
echo "*********************************************************************"

sudo tailscale up

echo "*********************************************************************"
echo "*********************************************************************"
echo "*********************************************************************"
echo "Tailscale setup complete"
echo "*********************************************************************"
echo "*********************************************************************"
echo "*********************************************************************"
