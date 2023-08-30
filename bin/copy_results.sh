#!/usr/bin/env bash

rsync -avzh \
	eudoxos:~/dev/hpb-project/results/ \
	results/

rsync -avzh \
	eudoxos:~/dev/tudat-bundle/results/ \
	results/
