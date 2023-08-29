#!/usr/bin/env bash

rsync -avzh --delete \
	--exclude /build --exclude /build-release --exclude /results --exclude "*perf*" --exclude ".*"	\
	../tudat-bundle/ \
	eudoxos:~/dev/tudat-bundle

rsync -avzh --delete \
	--exclude __pycache__ --exclude "*.pyc" --exclude "simulations/build" --exclude=".*" \
	--include "lropy/***" --include "simulations/***" --include "requirements.txt" \
	--exclude "*" \
	. \
	eudoxos:~/dev/hpb-project
