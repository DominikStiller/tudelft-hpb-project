#!/usr/bin/env bash

rsync -avzh --delete \
	--exclude /build --exclude /results --exclude ".*"	\
	../tudat-bundle/ \
	eudoxos:~/dev/tudat-bundle

rsync -avzh --delete \
	--exclude __pycache__ --exclude *.pyc --exclude ".*" --exclude /results \
	lropy/ \
	eudoxos:~/dev/lropy
