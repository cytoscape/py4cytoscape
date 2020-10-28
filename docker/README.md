## Docker environment 

Please do all your development in our development docker image:

```
docker pull mpgagebioinformatics/py4cytoscape:latest
```

* Create a folder to map to the container's user home folder
```
mkdir -p ~/py4cy-container
```

* Start the container from the latest version of the image
```
sudo docker run -d --network=host \
-v ~/py4cy-container:/home/py4cy --name py4cy-container \
-it mpgagebioinformatics/py4cytoscape:latest
```

* Alternatively you can start the container from a specific tag/version of the image
```
sudo docker run -d --network=host \
-v ~/py4cy-container:/home/py4cy --name py4cy-container \
-it mpgagebioinformatics/py4cytoscape:<tag>
```

* Connect to the running container
```
sudo docker exec -i -t py4cy-container /bin/bash
```

* Stop the container
```
sudo docker stop py4cy-container
```
----

## User account

User: `py4cy`

Pass: `cyto`

----

## Jupyter

Once you have connected to the running container you can start `jupyter` with
```
module load python
jupyter notebook --ip=0.0.0.0
```
A URL will be presented to you, and it should be pasted into your host's browser (Chrome  recommended).

----
## RStudio-server
Once you have connected to the running container you can start `Rstudio server` with
```
module load rlang
sudo rstudio-server start
```
You can then get access by connecting on your host's browser to [http://localhost:8787](http://localhost:8787).

For stopping the server use:
```
sudo rstudio-server stop
```

----

## X forward to enable Cytoscape

On a Mac install `socat` and `xquartz`:
```
brew install socat
brew install xquartz
```
Open Xquartz:
```
open -a Xquartz
```
Then navigate to XQuartz > Preferences > Security  and tick the box 'Allow connections from network clients'.

Check your ip address:
```
IP=$(ifconfig en0 | grep inet | awk '{ print $2 }' | grep -v ":" )
```
Start `socat`:
```
socat TCP-LISTEN:6000,reuseaddr,fork UNIX-CLIENT:\"$DISPLAY\"
```
an then start the container by adding the `-e DISPLAY=${IP}:0` argument. 

Complete example call:
```
IP=$(ifconfig en0 | grep inet | awk '{ print $2 }' | grep -v ":" ) && \
socat TCP-LISTEN:6000,reuseaddr,fork UNIX-CLIENT:\"$DISPLAY\" & \
docker run -d --network=host -e DISPLAY=${IP}:0 \
-v ~/py4cy-container:/home/py4cy --name py4cy-container \
-it mpgagebioinformatics/py4cytoscape:3.7.2
```
Then enter the container
```
docker exec -i -t py4cy-container /bin/bash
```
and
```
module load cytoscape
cytoscape.sh
```

----

## Development and Testing

Start Cytoscape on you host computer. You can also try to use Cytoscape from inside the container but be aware it is a less stable environment.

For testing py4cytoscape open a new terminal and get your host IP address, MAC example:
```
ifconfig en0 | grep inet | awk '{ print $2 }' | grep -v ":"
```
Start you container:
```
docker run -d --network=host -e DISPLAY=${IP}:0 \
-v <path_to_py4cytoscape>:/home/py4cy/py4cytoscape --name py4cy-container \
-it mpgagebioinformatics/py4cytoscape:latest
```
Enter the container:
```
docker exec -i -t py4cy-container /bin/bash
```
Load python:
```
module load python
```
Install py4cytoscape in developer mode:
```
cd pyt4cytoscape
python setup.py develop
```
Run the tests:
```
cd tests
export DEFAULT_BASE_URL='http://<YOUR_HOST_IP_ADDRESS>:1234/v1'
source runalltests.bat 
```



