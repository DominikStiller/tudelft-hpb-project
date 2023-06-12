#!/usr/bin/env bash

rsync -avzh --delete \
	--exclude /build --exclude /results --exclude /spice --exclude ".*"	\
	../tudat-bundle/ \
	eudoxos:~/dev/tudat-bundle

rsync -avzh --delete \
	--exclude __pycache__ --exclude *.pyc --exclude ".*" --exclude venv/ --exclude /results \
	lropy/ \
	eudoxos:~/dev/lropy

rsync -avzh --delete \
	--exclude __pycache__ --exclude *.pyc --exclude ".*" --exclude venv/ \
	analysis/ \
	eudoxos:~/dev/analysis
