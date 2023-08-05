CFLAGS=-DOPENGEODEDEBUG -Wall -g
all: generate-data-view generate-code compile


generate-data-view:
	asn1.exe -uPER -c DataView.asn

generate-data-view:
	asn1.exe -uPER -c DataView.asn



generate-code:
	../../generator.py --file pong.pr
	../../generator.py --file ping.pr

compile: generate-data-view
	gcc $(CFLAGS) -o ping-pong main.c ping_process.c pong_process.c

clean:
	rm -f *.o *~ ping_process.* pong_process.*
	rm -f ping-pong
	rm -f DataView.h DataView.c asn1crt.c asn1crt.h acn.c ber.c real.c xer.c
