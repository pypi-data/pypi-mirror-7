CFLAGS=-DOPENGEODEDEBUG -Wall 
all: generate-code compile

generate-code:
	../../generator.py --file pong.pr
	../../generator.py --file ping.pr

generate-data-view:
	asn1.exe -uPER -c DataView.asn

compile: generate-data-view
	gcc $(CFLAGS) -o ping integrate-ping.c ping_process.c
	gcc $(CFLAGS) -o pong integrate-pong.c pong_process.c

clean:
	rm -f *.o *~ ping_process.? pong_process.?
	rm -f pong ping
	rm -f DataView.h DataView.c asn1crt.c asn1crt.h acn.c ber.c real.c xer.c
