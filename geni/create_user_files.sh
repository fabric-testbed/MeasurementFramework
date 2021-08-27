#!/bin/bash
echo "Enter geni-slice name"
read geni_slice
echo "Pulling inventory file from $geni_slice"
/opt/gcf/examples/readyToLogin.py $geni_slice --useSliceAggregates --ansible-inventory -o
rm $geni_slice*
rm getversion*
python auto_host.py
