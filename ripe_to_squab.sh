#!/bin/bash

OUTPUT_FILE=tmp

echo "Make AS list."

echo "AS_Setting:" > $OUTPUT_FILE
sed -n -e "/path/,/]/{
	s/^  *//
	s/,//
	/path/d
	/]/d
	p
}
" $1 | sort -n | uniq | \
sed -e "s/[0-9][0-9]*/  &:\n\
    image: quagga/" >> $OUTPUT_FILE

echo "Make Peer info list."

echo "Peer_info:" >> $OUTPUT_FILE

PREV_AS=""
CONNECT_INFO_FILE=/tmp/connect
cat /dev/null > $CONNECT_INFO_FILE
sed -n -e "/path/,/]/{
	s/^  *//
	s/,//
	p
}
" $1 | uniq | while read line
do
	if [ "$line" = "\"path\": [" ]
	then
		:
	elif [[ "$line" =~ [0-9][0-9]* ]]
	then
		if [ -n "$PREV_AS" ]
		then
			if [ $line -lt $PREV_AS ]
			then
				echo "  - [$line, $PREV_AS]" >> $CONNECT_INFO_FILE
			else
				echo "  - [$PREV_AS, $line]" >> $CONNECT_INFO_FILE
			fi
		fi
		PREV_AS=$line
	elif [ "$line" = "]" ]
	then
		PREV_AS=""
	fi
done

cat $CONNECT_INFO_FILE | sort | uniq >> $OUTPUT_FILE
