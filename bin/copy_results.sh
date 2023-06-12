#!/usr/bin/env bash

rsync -avzh \
	eudoxos:~/dev/lropy/results/ \
	results/

rsync -avzh \
	eudoxos:~/dev/tudat-bundle/results/ \
	results/
