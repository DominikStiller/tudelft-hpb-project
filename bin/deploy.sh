#!/usr/bin/env bash

rsync -avzh --delete \
	--exclude /build --exclude /results --exclude ".*"	\
	../tudat-bundle/ \
	eudoxos:~/dev/tudat-bundle

