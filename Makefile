# Created by Andre Anjos <andre.anjos@idiap.ch> 
# Tue 17 Jan 2012 14:21:58 CET 

# Set this variable to change and test a different release directory
BOB_DIR="/idiap/group/torch5spro/nightlies/last"

prefix=BOB_DIR=$(BOB_DIR) ./shell.py --

all: clean

clean:
	@find lib -name "*.pyc" -print0 | xargs -0 rm -vf
	@find lib -name "*~" -print0 | xargs -0 rm -vf
	@find config -name "*.pyc" -print0 | xargs -0 rm -vf
	@find config -name "*~" -print0 | xargs -0 rm -vf
	@find script -name "*.pyc" -print0 | xargs -0 rm -vf
	@find script -name "*~" -print0 | xargs -0 rm -vf
	@find doc -name "*~" -print0 | xargs -0 rm -vf
	@find . -maxdepth 1 -name "*~" -print0 | xargs -0 rm -vf
	@if [ -d logs ]; then \
		find logs -name "*.o*" -o -name "*.e*" -print0 | xargs -0 rm -vf; \
		fi

.PHONY: clean
