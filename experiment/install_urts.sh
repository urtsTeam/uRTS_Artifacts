#!/bin/bash

function install_urts() {
    cd ../code/uRTS/
    mvn install -DskipTests
    cd ../../experiment/
}

install_urts