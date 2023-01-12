#!/usr/bin/env bash

rsync -avzh \
	eudoxos:~/dev/tudat-bundle/results/ \
	results/
