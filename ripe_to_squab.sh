#!/bin/bash

FILENAME=tmp

echo "AS_Setting:" > $FILENAME
sed -n -e "/path/,/]/{
	s/^  *//
	s/,//
	/path/d
	/]/d
	p
}
" $1 | sort -n | uniq | \
sed -e "s/[0-9][0-9]*/  &:\n\
    image: quagga/" >> $FILENAME
