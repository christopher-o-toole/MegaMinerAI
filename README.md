# MegaMinerAI

## Installation
### Ubuntu 16.04

#### Node.js Installation

The first step is to install Node.js version 8.X. Both the server and client depend on this library.
```
cd ~
curl -sL https://deb.nodesource.com/setup_8.x -o nodesource_setup.sh
sudo bash nodesource_setup.sh
sudo apt-get install nodejs
```
Check to see if installation was successful by running the following command:
```
nodejs -v
```
If the installation was successful, then the nodejs package should be at version ```v8.11.1``` or higher.

#### Add a SSH Key to your GitHub Account

The setup scripts for the MegaMinerAI repository all issue GitHub commands through SSH instead of HTTPS. Therefore, you will need to [add an SSH key to your GitHub account](https://help.github.com/articles/adding-a-new-ssh-key-to-your-github-account/) if you haven't already.


####  MegaMinerAI Repo Installation

We're almost ready to run MegaMinerAI matches on our own machine! We will now install the repository provided by SIG-Game.

Start off by cloning Cadre and all its submodules:
```
git clone git@github.com:siggame/Cadre.git
cd Cadre
./init.sh
```
Then install the Cerveau game server with npm:
```
cd Cerveau
npm install
```
Ensure that the server was installed sucessfully by running the following command:
```
node main.js
```
The server output should look something like this:
![cerveau_success](https://raw.githubusercontent.com/christopher-o-toole/MegaMinerAI/master/cerveau_success_better.png)

You should now be ready to run matches over localhost!

#### Test your Installation
Run the server as shown in the last section, and then open up two terminals in the ```Joeur.py``` folder. You may start a game by running ```python3 main.py <game-name>``` in each terminal. 

![installation_complete](https://raw.githubusercontent.com/christopher-o-toole/MegaMinerAI/master/installation-complete.png)

