# Overview Service
Gets information about all the installed services.

## Get a list of all services
readmes = mf.info("overview")["services"]
print(readmes)

# Get the READMEs for all services.
readmes = mf.info("overview")["readmes"]
print(readmes)