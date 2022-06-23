#!/bin/bash

./fetch.sh

http-server --port "$(cat .port)"