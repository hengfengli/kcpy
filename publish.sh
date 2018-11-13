#!/bin/bash

export $(cat twine.env | xargs)

twine upload dist/*
