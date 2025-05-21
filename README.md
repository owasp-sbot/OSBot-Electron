# OSBot__Repo_Template

## Repo details

![Current Release](https://img.shields.io/badge/release-v0.2.4-blue)

This version worked ok on the Electron site of things, opened up the FastAPI and allowed the remote access via Playwright to the opened browser, but the problems started to occur when looking at the deployment options, since now we have to have a node and a python deployment 

The creation of the Electron app is working ok in the current GitHub actions, but adding and packaging the python code was looking messy (specially when trying to keep the node code as small as possible)

The key concern is that even with all this working, we will still have the complexity of having two complete execution environments (node and Python)