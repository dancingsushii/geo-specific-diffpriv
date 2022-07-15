#!/bin/bash

gcloud config set project peng-geodp
gcloud config set compute/region europe-west3
gcloud config set compute/zone europe-west3-c
gcloud compute project-info describe