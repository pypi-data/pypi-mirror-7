asn1.exe -c -equal -o dataview/ -typePrefix asn1Scc DataView.asn
buildsupport -i InterfaceView.aadl -d DataView.aadl --smp2 -o tmp
cp tmp/iv.py .


