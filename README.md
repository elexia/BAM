# BAM
BAM stands for Bigfix Automation Module, and was created for Stanford University's Information Security office. It can create queries and retrieve information from the Bigfix Webreports Database using an independent library called SUDS. 
Documentation can be found here: 
https://asconfluence.stanford.edu/confluence/display/SECOPS/BigFix+Automation+Module

##Cool Features
###Query Creation
BAM has to talk to the BF Webreports database, and it does so by creating queries in Relevance Language. Given a list of filters, a list of returns, and a search property (usually "computers"), it can generate a complex query to return the information you need.
###Complex Parsing
Because BAM saves all of its returns into an iterable object, it parses a wide array of properties. This is possible using Single and Multiple property detection.
