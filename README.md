# pycsw4django

# Usage
- create a virtual environment with python3 as default python interpreter.
- activate it
- run `./install.sh`
- open your browser at the following link:

  [http://localhost.localdomain:8000/csw?mode=oaipmh&verb=ListRecords&metadataPrefix=oai_dc](http://localhost.localdomain:8000/csw?mode=oaipmh&verb=ListRecords&metadataPrefix=oai_dc)

if all go well you can see something like:
```
<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<!-- pycsw 2.1.dev0 -->
<oai:OAI-PMH xmlns:oai="http://www.openarchives.org/OAI/2.0/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.openarchives.org/OAI/2.0/ http://www.openarchives.org/OAI/2.0/OAI-PMH.xsd"><oai:responseDate>2017-10-26T14:05:47Z</oai:responseDate><oai:request metadataprefix="oai_dc" verb="ListRecords">http://localhost.localdomain:8000/csw?mode=oaipmh</oai:request><oai:ListRecords><oai:resumptionToken completeListSize="0" cursor="-1">0</oai:resumptionToken></oai:ListRecords></oai:OAI-PMH>
```