# Changes Made
	- Removed roles
		- base
	- Changed to only install needed packages
		- only on the nodes that need it

# Times Per Number of Worker nodes and OS's:
	Test two worker (11 Nov 2021):
		- Ubuntu 20.04 and CentOs 8
		- Meas_Net, Meas_Node, and Meas_NGINX running CentOs 8 
		- real	20m15.562s
		- user	0m6.836s
		- sys	0m3.814s

	Test three worker (11 Nov 2021):
		- Ubuntu 20.04, CentOs 7 and CentOs 8
		- Meas_Net, Meas_Node, and Meas_NGINX running CentOs 7
		- real	20m56.562s
		- user	0m7.801s
		- sys	0m5.131s


