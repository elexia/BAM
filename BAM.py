# Author: Elexia Pierre
# -*- coding: utf-8 -*-

import getpass
from dateutil.parser import parse
import suds
from suds.client import Client
from suds.transport.https import HttpAuthenticated

#ABOUT QUERY_CREATOR
#Query_creator makes it possible to retrieve information from Bigfix by creating a customized query, using SOAP protocol, and inputtiung user credentials to retreive the information.
#The application can then save this information into variable python objects. (string, int, datetime, etc.) 
#The only library that needs to be downloaded is the SUDS python library for SOAP communication to Bigfix (https://fedorahosted.org/suds/)
#Created by: Elexia Pierre

#Opens program log to a file
f = open("BAM LOGS", "w")

#A function for creating queries with user input. Returns the query class instance.
#For the actual query, enter "QueryName.Query"
def input_query():
    f.write("<input_query> : <no parameters> \n")
    return_value = []
    filter = []
    print "Now creating relevance query."
    return_input = " "
    print "Please enter the return value: (Press enter again when finished)\n"
    while (return_input != ""):
        return_input = raw_input()
        returnvalue.append(return_input)
    returnvalue.pop()
    filter_input = " "
    print "Please enter any filters: (Press enter again when finished)\n"
    while (filter_input != ""):
        filter_input = raw_input()
        filter.append(filter_input)
    filter.pop()
    print "Please enter what you would like to search: \n"
    search = raw_input()
    myquery = query(returnvalue, filter, search)
    print "Success!"
    myquery.printQuery()
    f.write("<input_query> : <returning relevance_query> \n")
    return myquery


def input_soap(*arg):
    f.write("<input_soap> : <no required parameters, one optional parameter : relevance \n")
    '''Allows the user to input a relevance query and credentials, then retrieve
    returned information (result)
    Relevance argument should be passed into the functon parameters if created
    and stored into a python variable (ex: when usnig input_query)'''
    # get user input
    username = raw_input("Enter username: ")
    password = getpass.getpass("Enter password: ")
    url = raw_input("Enter website: ")
    if (arg is not None):
        relevance = str(*arg)
    else:
        relevance = raw_input("Enter relevance: ")
    result = soap_query(username, password, url, relevance)
    print "Success!"
    f.write("<input_soap> : <returning result> \n")
    return result

class relevance_query:
    '''RelevanceQuery is a class that will create the query, and hold necessary
    query information'''

    #Used by "create" class to figure out what return properties are requested
    property_list = [] 
    #Used by "create" class to figure out what datatypes to save properties as
    property_type = [] 
    actions = ["contains", "does not contain", "starts with", "ends with", "is", "is not"]

    Query = "("
    temp_return = "("
    temp_search = " "
    temp_filters = "( "

    #The constructor creates the query as a string given return values and return data types
    def __init__(self, returnvalues, filtervalues, search):
        '''return_values: should come in a list (any order)

        return_values can also take in the optional variable type to be
        returned. Supports int, date, datetime, and string (default). 
        Type "as [type]" after return property.
            Ex: ["Average Time in idle state in hours/day", "as int"]
            Ex: ["MAC Addresses", "Computer Name", "OS"]
        
        filter: values should come in a list of 3 occurences 
        (bes property, modifier, value, *or)
            Ex: ["Computer Name", "starts with", "iso-", "MACAddresses", 
                 "does not contain", "00-50"]
        *filters can also make use of "or"s. (Optional)
        
        ORs can make use of a new filter:
            Ex: ("MAC Addresses", "contains", 2, "OR", "Computer Name", 
                 "starts with", "iso-")
        A filter with the first value derived:
            Ex: ("MAC Addresses", "contain", 2, "OR", "start with", 0) 
        Or a filter with two values derived:
            Ex: (MAC Addresses, contains, 2, "OR", 3)
        
        Because filters can be a variable lengh, and depend on ANDs and ORs, 
        there are many cases.

        search: should come in a string
        Ex: "Computers"
        '''        
        f.write("<relevance_query constructor> : <expecting returns, filters, and search values to create a query> \n")

        #  Check through each filter value to find keywords like OR, and create the finalized string
        filters = []
        for size_filters in range(0, len(filtervalues)):
            if (type(filtervalues[size_filters]) is list):
                for each_filter in range(0, len(filtervalues[size_filters])):
                    filters.append(filtervalues[size_filters][each_filter])
            else:
                filters.append(filtervalues[size_filters])
                
        for each_filter in range(0, len(filters)):
            filters[each_filter] = filters[each_filter].lower()

        delete_index = []
        # adds "as ____" statements to return_types list, places string as 
        # datatype if no "as ____" statement & begins creating query
        for each in range(0, len(returnvalues)-1):
            if (returnvalues[each][0:2] == "as"):
                self.property_type.pop()
                self.property_type.append(returnvalues[each][3:])
                delete_index.append(each)
                           
            else:
                self.property_type.append("string")
                self.Query = self.Query + " values of results ( bes property \"" + returnvalues[each] + "\", it),"
                self.temp_return = self.temp_return + " values of results ( bes property \"" + returnvalues[each] + "\", it), \n"

        if (returnvalues[len(returnvalues)-1][0:2] == "as"):
            self.property_type.pop()
            self.property_type.append(returnvalues[len(returnvalues)-1][3:])
            delete_index.append(len(returnvalues)-1)
            self.Query = self.Query[:-2] + " ) )"
            self.temp_return = self.temp_return[:-4] + " ) )"

        else:
            self.property_type.append("string")
            self.Query = self.Query + "  values of results ( bes property \"" + returnvalues[len(returnvalues)-1] + "\", it) )"
            self.temp_return = self.temp_return + " values of results ( bes property \"" + returnvalues[len(returnvalues)-1] + "\", it) )"

        #gets rid of "as ____" statements in returnvalues list
        for each in range (0, len(delete_index)): 
            if (len(delete_index) == 1):
                returnvalues.pop(delete_index[0])
            else:
                for each in range(1, len(delete_index)):
                    delete_index[each] = delete_index[each] - 1
                returnvalues.pop(delete_index[0])
                delete_index.pop(0)

        self.property_list = returnvalues 
  
        self.Query = self.Query +  " of bes " + search + " whose " #Entering in the search value.
        self.temp_search = self.temp_search +  " of bes " + search + " whose "

        self.Query = self.Query + "( "

        increment = 0
        base_index = 0

        while (increment < len(filters)):
            # Adds OR and subtracts previous "AND" from string -- 

            if (filters[increment] == "or"):
                counter = 0
                while ( counter != -1 ):
                    if (len(filters) - 1 <= increment + 3 ):
                        if(len(filters) - 1 == increment + 3 and filters[increment+2] != "or" and filters[increment+2] != "and" ):
                            self.Query = self.Query[:-5] + " OR " 
                            self.temp_filters = self.temp_filters[:-7] + " OR \n\n"
                            increment = increment + 1
                            counter = -1
                            break
                        elif (len(filters) - 1 == increment + 2):
                            # Check chain finds the old filter to base the new OR filter on 
                            #(ex: "computer name", "starts with", "iso", "OR", "a") 
                            #Check chain will create the "computer name starts with a" filter based on "computer name starts with iso".
                            base_index= check_chain(filters, increment)
                            self.Query = self.Query[:-5] + " OR ( value of result (bes property \"" + filters[base_index-3] + "\", it) as lowercase " + filters[increment+1] + " \"" + filters[increment+2] + "\" ) AND "
                            self.temp_filters = self.temp_filters[:-7] + " OR \n\n ( value of result (bes property \"" + filters[base_index-3] + "\", it) as lowercase " + filters[increment+1] + " \"" + filters[increment+2] + "\" ) AND \n\n"
                            increment = increment + 3
                            counter = -1
                            break
                        elif (len(filters) - 1 == increment + 1):
                            base_index = check_chain(filters, increment)
                            self.Query = self.Query[:-5] + " OR ( value of result (bes property \"" + filters[base_index-3] + "\", it) as lowercase " + filters[base_index-2] + " \"" + filters[increment+1] + "\" ) AND "
                            self.temp_filters = self.temp_filters[:-7] + " OR \n\n ( value of result (bes property \"" + filters[base_index-3] + "\", it) as lowercase " + filters[base_index-2] + " \"" + filters[increment+1] + "\" ) AND \n\n"
                            increment = increment + 2
                            counter = -1
                            break

                        else:
                            base_index = check_chain(filters, increment)
                            self.Query = self.Query[:-5] + " OR ( value of result (bes property \"" + filters[base_index-3] + "\", it) as lowercase " + filters[base_index-2] + " \"" + filters[increment+1] + "\" ) AND "
                            self.temp_filters = self.temp_filters[:-7] + " OR \n\n ( value of result (bes property \"" + filters[base_index-3] + "\", it) as lowercase " + filters[base_index-2] + " \"" + filters[increment+1] + "\" ) AND \n\n"
                            increment = increment + 2
                            counter = -1
                            break

                    else:
                        if (filters[increment + 2] in self.actions):
                            self.Query = self.Query[:-5] + " OR " 
                            self.temp_filters = self.temp_filters[:-7] + " OR \n\n"
                            increment = increment + 1
                            counter = -1
                        elif (filters[increment + 1] in self.actions):
                            base_index = check_chain(filters, increment)
                            self.Query = self.Query[:-5] + " OR ( value of result (bes property \"" + filters[base_index-3] + "\", it) as lowercase " + filters[increment+1] + " \"" + filters[increment+2] + "\" ) AND "
                            self.temp_filters = self.temp_filters[:-7] + " OR \n\n ( value of result (bes property \"" + filters[base_index-3] + "\", it) as lowercase " + filters[increment+1] + " \"" + filters[increment+2] + "\" ) AND \n\n"
                            increment = increment + 3
                            counter = -1
                        elif ((filters[increment + 2] == "or") or (filters[increment +2] == "and") or (filters[increment + 3] in self.actions)):
                            base_index = check_chain(filters, increment)
                            self.Query = self.Query[:-5] + " OR ( value of result (bes property \"" + filters[base_index-3] + "\", it) as lowercase " + filters[base_index-2] + " \"" + filters[increment+1] + "\" ) AND "
                            self.temp_filters = self.temp_filters[:-7] + " OR \n\n ( value of result (bes property \"" + filters[base_index-3] + "\", it) as lowercase " + filters[base_index-2] + " \"" + filters[increment+1] + "\" ) AND \n\n"
                            increment = increment + 2
                            counter = -1
                        else:
                            counter = counter + 1
            elif(filters[increment].lower() == "and"):
                counter = 0
                while (counter != -1):
                    if (increment + 3 < len(filters)-1 and filters[increment+2] != "and" and filters[increment+2] != "or"):
                        if (filters[increment+1] in self.actions):
                            base_index = check_chain(filters, increment) #Uses check_chain to prevent errors with "or" chain-ing (and decrement "increment" variablethe right amount)
                            self.Query = self.Query[:-5] + " AND ( value of result (bes property \"" + filters[base_index-3] + "\", it) as lowercase " + filters[increment+1] + " \"" + filters[increment+2] + "\" ) AND "
                            self.temp_filters = self.temp_filters[:-7] + "AND \n\n ( value of result (bes property \"" + filters[base_index-3] + "\", it) as lowercase " + filters[increment+1] + " \"" + filters[increment+2] + "\" ) AND \n\n"
                            increment = increment + 3
                            counter = -1
                        elif (filters[increment+2].lower() in self.actions):
                            self.Query = self.Query[:-5] + " AND " 
                            self.temp_filters = self.temp_filters[:-7] + " AND \n\n"
                            increment = increment + 1
                            counter = -1

                        elif (filters[increment+2].lower == "and" or filters[increment+2].lower == "or" or (filters[increment+3].lower() in self.actions)):
                            base_index = check_chain(filters, increment)
                            self.Query = self.Query[:-5] + " OR ( value of result (bes property \"" + filters[base_index-3] + "\", it) as lowercase " + filters[base_index-2] + " \"" + filters[increment+1] + "\" ) AND "
                            self.temp_filters = self.temp_filters[:-7] + " OR \n\n ( value of result (bes property \"" + filters[base_index-3] + "\", it) as lowercase " + filters[base_index-2] + " \"" + filters[increment+1] + "\" ) AND \n\n"
                            increment = increment + 2
                            counter = -1
                        else:
                            base_index = check_chain(filters, increment)
                            self.Query = self.Query[:-5] + " OR ( value of result (bes property \"" + filters[base_index-3] + "\", it) as lowercase " + filters[base_index-2] + " \"" + filters[increment+1] + "\" ) AND "
                            self.temp_filters = self.temp_filters[:-7] + " OR \n\n ( value of result (bes property \"" + filters[base_index-3] + "\", it) as lowercase " + filters[base_index-2] + " \"" + filters[increment+1] + "\" ) AND \n\n"
                            increment = increment + 2
                            counter = -1

                    else: #Added in to stop index errors (checking past index size)
                        if (filters[increment + 2] in self.actions):
                            self.Query = self.Query[:-5] + " AND " 
                            self.temp_filters = self.temp_filters[:-7] + " AND \n\n"
                            increment = increment + 1
                            counter = -1
                        elif (filters[increment + 1] in self.actions):
                            base_index = check_chain(filters, increment)
                            self.Query = self.Query[:-5] + " AND ( value of result (bes property \"" + filters[base_index-3] + "\", it) as lowercase " + filters[increment+1] + " \"" + filters[increment+2] + "\" ) AND "
                            self.temp_filters = self.temp_filters[:-7] + " AND \n\n ( value of result (bes property \"" + filters[base_index-3] + "\", it) as lowercase " + filters[increment+1] + " \"" + filters[increment+2] + "\" ) AND \n\n"
                            increment = increment + 3
                            counter = -1
                        elif ((filters[increment + 2] == "or") or (filters[increment +2] == "and") or (filters[increment + 3] in self.actions)):
                            base_index = check_chain(filters, increment)
                            self.Query = self.Query[:-5] + " AND ( value of result (bes property \"" + filters[base_index-3] + "\", it) as lowercase " + filters[base_index-2] + " \"" + filters[increment+1] + "\" ) AND "
                            self.temp_filters = self.temp_filters[:-7] + " AND \n\n ( value of result (bes property \"" + filters[base_index-3] + "\", it) as lowercase " + filters[base_index-2] + " \"" + filters[increment+1] + "\" ) AND \n\n"
                            increment = increment + 2
                            counter = -1
                        else:
                            counter = counter + 1

            elif(filters[increment].lower() == "and*"):
                for all in range (increment+1, filters[len(filters)-1]):
                    assert(filters[all].lower() != "or")
                    assert(filters[all].lower() != "and")
                
                base_index = check_chain(filters, increment)
                for each in range (increment+1, filters[len(filters)-1]):
                    self.Query = self.Query[:-5] + " AND ( value of result (bes property \"" + filters[base_index-3] + "\", it) as lowercase " + filters[base_index-2] + " \"" + filters[each] + "\" ) AND "
                    self.temp_filters = self.temp_filters[:-7] + " AND \n\n ( value of result (bes property \"" + filters[base_index-3] + "\", it) as lowercase " + filters[base_index-2] + " \"" + filters[each] + "\" ) AND \n\n"
                increment = len(filters)-1      
                          
            elif(filters[increment].lower() == "or*"):
                for all in range (increment+1, len(filters)-1):
                    assert(filters[all].lower() != "or")
                    assert(filters[all].lower() != "and")
                
                base_index = check_chain(filters, increment)
                for each in range (increment+1, len(filters)-1):
                    self.Query = self.Query[:-5] + " OR ( value of result (bes property \"" + filters[base_index-3] + "\", it) as lowercase " + filters[base_index-2] + " \"" + filters[each] + "\" ) AND "
                    self.temp_filters = self.temp_filters[:-7] + " OR \n\n ( value of result (bes property \"" + filters[base_index-3] + "\", it) as lowercase " + filters[base_index-2] + " \"" + filters[each] + "\" ) AND \n\n"
                increment = len(filters)

            else:    
                
                self.Query = self.Query + "( value of result ( bes property \"" + filters[increment] +"\", it) as lowercase " + filters[increment+1] + " \"" + filters[increment+2] + "\" ) AND "
                self.temp_filters = self.temp_filters + "   ( value of result ( bes property \"" + filters[increment] +"\", it) as lowercase " + filters[increment+1] + " \"" + filters[increment+2] + "\" ) AND \n\n"
                increment = increment + 3


        self.Query = self.Query[:-4] + ")"
        self.temp_filters = self.temp_filters[:-6] + "\n)"
        f.write("<relevance_query constructor> : <exiting> \n")


    def return_query(self,):
        f.write("<return_query> : <no parameters> \n")
        '''Returns the query string instead of the class instance itself.'''
        f.write("<return_query> : <returning the query> \n")
        return self.Query

    def file_readable_query(self,):
        '''Files a query in readable format from the python terminal.
        This function is the reason all of the strings were doubled, because it 
        allows the strings to be divided into return, filter, and search values 
        for easy filing.
        '''
        f.write("<file_readable_query> : <no parameters> \n")
        newfile.open("ReadableQuery", "w")
        newfile.write(self.temp_return[0] + "\n")
        newfile.write( self.temp_return[2:len(self.temp_return)-2] + "\n")
        newfile.write( self.temp_return[len(self.temp_return)-1] + "\n")
        newfile.write( self.temp_search + "\n")
        newfile.write( self.temp_filters[0] + "\n")
        newfile.write( self.temp_filters[2:len(self.temp_filters)-2] + "\n")
        newfile.write( self.temp_filters[len(self.temp_filters)-1] )
        f.write("<file_readable_query> : <exiting> \n")

    def print_readable_query(self,):
        '''Prints a query in readable format from the python terminal.
        This function is the reason all of the strings were doubled, because it 
        allows the strings to be divided into return, filter, and search values 
        for easy printing.
        '''
        f.write("<print_readable_query> : <no parameters> \n")
        print self.temp_return[0] + "\n"
        print self.temp_return[2:len(self.temp_return)-2] + "\n"
        print self.temp_return[len(self.temp_return)-1] + "\n"
        print self.temp_search + "\n"
        print self.temp_filters[0] + "\n"
        print self.temp_filters[2:len(self.temp_filters)-2] + "\n"
        print self.temp_filters[len(self.temp_filters)-1]
        f.write("<print_readable_query> : <exiting> \n")
    
    def print_query(self,):
        f.write("<print_query> : <no parameters> \n")
        '''Prints the query in literal string format, how it will be passed into 
        soap_query'''
        f.write("<print_query> : <exiting> \n")
        print self.Query


    def return_properties(self):
        f.write("<return_properties> : <no parameters> \n")
        '''Quick functions for the object creator that retuns the "return properties" and "property types" requested into the query class constructor
        Useful for creating a saveable list with the correct attributes'''
        f.write("<return_properties> : <returning property_list> \n")
        return self.property_list

    def returnproperty_types(self):
        f.write("<returnproperty_types> : <no parameters> \n")
        f.write("<returnproperty_types> : <returning property_type> \n")
        return self.property_type
        
#QUERY HELPER FUNCTIONS:


def check_chain(filters, index):
    f.write("<check_chain> : <expecting filters and index to find base filter> \n")
    '''
    Check chain finds the old filter to base the new OR filter on 
      (ex: "computer name", "starts with", "iso", "OR", "a") 
      Check chain will create the "computer name starts with a" filter based on "computer name starts with iso".
      '''

    base_index = index

    if(filters[base_index - 2].lower() == "or" or filters[base_index - 2].lower() == "and"):
        base_index = base_index - 2
        return check_chain(filters, base_index )
    elif(filters[base_index - 3].lower() == "or" or filters[base_index - 3].lower() == "and"):
        base_index = base_index - 3
        return check_chain(filters, base_index )
    else:
        f.write("<check_chain> : <returning the correct index> \n")
        return base_index 

def soap_query(username, password, website, relevance):
    '''Soap Query takes in login, username, website, and relevance expression. It returns a list of strings as the Relevance result.'''

    f.write("<soap_query> : <expecting credentials, website and relevance to get results from BigFix> \n")
    username = username
    password = password
    website = website
    relevance = str(relevance)

    credentials = dict(username = username, password = password)
    t = HttpAuthenticated(**credentials)
    rel = Client((website + "?wsdl"), location = website, transport=t)
    rel.set_options(port='RelevancePort')
    result = rel.service.GetRelevanceResult(relevance, username, password)
    #Fix right/left apostrophe errors
    for each in range(0, len(result)):
        result[each] = unicode(result[each]).replace(u'\u2019', u'\u0027').replace(u'\u2018', u'\u0027')
        #result[each] = result[each].encode('utf-8')
    f.write("<soap_query> : <returning the results> \n")
    return result


#PRINTING/FILE RESULT FUNCTIONS

def print_result(result):
    f.write("<print_result> : <takes in result to print out> \n")
    '''Will print the result of the query. Separates list elements into 
    different lines of output.'''
    result = result
    for each in range(0, len(result)):
        print (result[each])
    f.write("<print_result> : <exiting> \n")

def file_result(name, result):
    '''Saves the results of the query into an existing file.
    Separates list elements into different lines of output. If the result is a 
    string, simply output on one line. If result is a set, output as a list.
    Name = Filepath, Result = Query Result
    '''
    f.write("<file_result> : <expecting name of file and result to print out> \n")
    file = open(name, 'w')
    if (type(result) is list):
        for each in range(0, len(result)):
            file.write(result[each])
            file.write("\n")
    elif (type(result) is str):
        file.write(result)
    elif (type(result) is set):
        result = list(result)
        for each in range(0, len(result)):
            file.write(result[each])
            file.write("\n")
    f.write("<file_result> : <exiting> \n")

def new_file_result(name, result):
    '''Saves the results of the query into a newly created file. 
    Separates list elements into different lines of output. If result is a 
    singular string, simply output on one line. If result is a set, output as a 
    list.
    Name = Filepath (Default filepath is wherever soap_query is located) 
    Result = Query Result
    '''

    f.write("<new_file_result> : <expects name of file and result to print out> \n")
    file = open(name, 'w+')
    if (type(result) is list):
        for each in range(0, len(result)):
            file.write(result[each])
            file.write("\n")
    elif (type(result) is str):
        file.write(result)
    elif (type(result) is set):
        result = list(result)
        for each in range(0, len(result)):
            file.write(result[each])
            file.write("\n")
    f.write("<new_file_result> : <exiting> \n")


class create(object):
    '''Create is a class which creates a python list containing each result, 
    given the original relevance query and the result.

    If the relevance query was not made with BAM function 'relevance_query', the parameter for query 
    should be "None" and a list of property names and wanted return types should be passed in as a third parameter.

        Ex: create(None, myresult, ["Computer Name", "string", "Computer ID", "string", "Last Report Time", "datetime"]) 
    '''
    #Objects is a list of parallel lists which contain the return values from a bigfix query
    Objects = [] 
    num_properties = 0
    name_properties = []
    type_properties = [] 
    return_types = [] #The data types (string, int, etc) of each return property
    dedup_query = "" #Used in dedup function

    def __init__(self, query, result, *arg):
        f.write("<create> : <Expecting query instance and result (or result and return types) to parse result> \n")

        
        if (arg is not ()): #Reading in the manual query list
            counter = 0
            while (counter < len(arg)):
                self.name_properties.append(arg[counter])
                self.return_types.append(arg[counter])
                counter = counter + 2
            self.num_properties = len(self.name_properties)

        else: #Reading in through normal query means.
            self.dedup_query = query.return_query()
            #Return properties passed through original query instance
            self.name_properties = list(query.return_properties()) 
            self.num_properties = len(query.return_properties())
            #Return property types passed through original query instance
            self.return_types = list(query.returnproperty_types()) 

        if (result == []):
            print "ERROR: No result returned. \n\n\n"   

        if (self.num_properties == 1): 
            #If there is only one return propety instance Multiple and Single 
            #functions can be used
            for each in range (0, len(result[0])):
                if (result[0][each] == ","):
                    self.Objects = Multiple(result)
                    break
                elif (each == len(result[0])-1):
                    self.Objects = Single(result)
                    break

        else:

            for each in range (0, len(result)):
               self.Objects.append([])
            #Identify single or multi property for each return property
            self.type_properties = return_types(result, self.num_properties) 
            for each_property in range (0, self.num_properties): #For every property
                for each_system in range (0, len(result)): #Once per returned computer
                    if (self.type_properties[each_property] == "S"):
                        result[each_system] = remove_single(self.Objects[each_system], result[each_system]) 
                    elif (self.type_properties[each_property] == "M"):
                        result[each_system] = remove_multi(self.Objects[each_system], result[each_system])

        if (self.num_properties == 1):
            for each in range(0, len(self.Objects)):
                if (self.return_types[0] == "string"): #Default
                    if (type(self.Objects[each]) is unicode):                 
                        if (self.Objects[each][0] == " "):
                            self.Objects[each] = self.Objects[each][1:]

                if (self.return_types[0] == "int"):
                    self.Objects[each] = int(float(self.Objects[each]))

                if (self.return_types[0] == "float"):
                    self.Objects[each] = float(self.Objects[each])

                # Datetime are saved into ['day of week', 
                #                          'day mon year time +0000 '] 
                if (self.return_types[0] == "datetime"):
                    if (self.Objects[each][0].find("Warning") is not -1):
                        break
                    else:
                        self.Objects[each][1] = parse(self.Objects[each][1])

                # Dates are saved into ['day month year'] format
                if (self.return_types[0] == "date"):
                    self.Objects[each] = parse(self.Objects[each])
        else:
            #The same premise, with more than one property
            for index in range(0, len(self.Objects)):
                for property in range(0, len(self.Objects[index])):
                    for result in range(0, len(self.Objects[index][property])):
                        if (self.return_types[property] == "string"): 
                            break
                
                        if (self.return_types[property] == "int"):
                            self.Objects[index][property][result] = int(float(self.Objects[index][property][result]))
                            break

                        if (self.return_types[property] == "float"):
                            self.Objects[index][property][result] = float(self.Objects[index][property][result])
                            break

                        if (self.return_types[property] == "datetime"):
                            self.Objects[index][property][result] = parse(self.Objects[index][property][result])
                            break

                        if (self.return_types[property] == "date" and self.Objects[index][property][result].lower() != "n/a"):
                            self.Objects[index][property][result] = parse(self.Objects[index][property][result])
                            break

        f.write("<create> : <exiting> \n")

    #Removes duplicates caused by a single property with more than one value per system
    def dedup(self, dupProperty):
        f.write("<create.dedup> : <expects duplicate property to accurately deduplicate Objects> \n")

        temp_query = create.dedup_query[:1] + " values of results (bes property \"Computer ID\", it), " + self.dedup_query[2:]
        u = raw_input("Enter username: ")
        p = getpass.getpass("Enter password: ")
        url = raw_input("Enter URL: ")
        temp_result = soap_query(u, p, url, temp_query)
        ComputerID = []

        for each in range (0, len(temp_result)):
             ComputerID.append(temp_result[each][0:7])

        for each in range(0, self.num_properties):
            if (self.name_properties[each].lower() == dupProperty.lower()):
                indexDup = each
                break
            elif (each == self.num_properties-1):
                print "ERROR. dupProperty not in property list"
                return -1
            else:
                continue

        delete_index = []
        temp_list = []
        index = 0
        for counter in range(0, len(self.Objects)):
            if (counter == len(self.Objects) - 1):#If its the end of the list
                if (temp_list != []): #If temp_list isnt empty, this is a duplicate
                    delete_index.append(counter)
                    for each in range (0, len(temp_list)):
                        self.Objects[index][indexDup].append(temp_list[each])
                else:
                    continue
            elif (ComputerID[counter] != ComputerID[counter+1]):
                for each in range (0, len(temp_list)):
                    self.Objects[index][indexDup].append(temp_list[each])
                while (temp_list != []):
                    temp_list.pop()
            else: #If the computer IDS match in front, and its not the end of the list
                if (ComputerID[counter-1] != ComputerID[counter] or counter == 0):
                    index = counter
                delete_index.append(counter+1)
                temp_list.append(self.Objects[counter+1][indexDup][0])

        for each in range (0, len(delete_index)):
            if (len(delete_index) == 1):
                self.Objects.pop(delete_index[0])
            else:
                for all in range(1, len(delete_index)):
                    delete_index[all] = delete_index[all] - 1
                self.Objects.pop(delete_index[0])
                delete_index.pop(0)

        f.write("<create.dedup> : <exiting> \n")

    def return_Objects(self):
        '''Returns Objects from create class'''
        f.write("<return_Objects> : <no parameters. returning Objects.> \n")
        f.write("<return_Objects> : <returning Objects> \n")
        return Objects

    def print_index(self):
        '''Prints out objects per Object index in blocks
        (by individual computer)'''

        f.write("<print_index> : <no parameters. printing out Objects. > \n")
        for index in range(0, len(self.Objects)):
            for value in range (0, len(self.Objects[index])):
                    if (len(self.Objects[index]) > 1 and type(self.Objects[index][value]) is unicode):
                        print self.Objects[index][value].replace(u"\u2018", "'").replace(u"\u2019", "'")
                    elif (len(self.Objects[index]) > 1 and type(self.Objects[index][value]) is list):
                        for z in range (0, len(self.Objects[index][value])):
                            print self.Objects[index][value][z].replace(u"\u2018", "'").replace(u"\u2019", "'")
                    elif (len(self.Objects[index]) == 1):
                        print self.Objects[index][value].replace(u"\u2018", "'").replace(u"\u2019", "'")
            print "\n"
        f.write("<print_index> : <exiting> \n")

    def file_index(self):
        '''Files out objects per Object index in blocks
        (by individual computer)'''

        f.write("<file_index> : <no parameters. filing out objects. > \n")
        newfile.open("Objects_by_index", "w")
        for index in range(0, len(self.Objects)):
            for value in range (0, len(self.Objects[index])):
                    if (len(self.Objects[index]) > 1 and type(self.Objects[index][value]) is unicode):
                        newfile.write( self.Objects[index][value].replace(u"\u2018", "'").replace(u"\u2019", "'") )
                    elif (len(self.Objects[index]) > 1 and type(self.Objects[index][value]) is list):
                        for char in range (0, len(self.Objects[index][value])):
                            newfile.write( self.Objects[index][value][char].replace(u"\u2018", "'").replace(u"\u2019", "'") )
                    elif (len(self.Objects[index]) == 1):
                        newfile.write( self.Objects[index][value].replace(u"\u2018", "'").replace(u"\u2019", "'") )
            newfile.write( "\n")
        f.write("<file_index> : <exiting> \n")

    def print_each(self):
        f.write("<print_each> : <no parameters. printing out Objects.> \n")
        for each in range (0, len(self.Objects)):
            print self.Objects[each]
            print "\n"
        f.write("<print-each> : <exiting> \n")

    def file_each(self):
        f.write("<file_each> : <no parameters. filing out Objects.> \n")
        newfile.open("Object_by_each", "w")
        for each in range (0, len(self.Objects)):
            newfile.write( self.Objects[each])
            newfile.write( "\n" )
        f.write("<print-each> : <exiting> \n")


#OBJECT CREATOR HELPER FUNCTIONS

def remove_single(destination, result):
    '''Removes one single property from a string (up to ","), 
    returns the string, and appends the removed value to the destination 
    (as a string)
    '''
    f.write("<remove_single> : <expects a destination and result. appends to the destination, cuts off the result> \n")
    temp = []
    if (result.find(",") == -1):
        temp.append(result)
        destination.append(temp)
        result = ""
        f.write("<remove_single> : <returning result> \n")
        return result
    else:
        cutoff = result.index(",")
        temp.append(result[:cutoff])
        destination.append(temp)
        result = result[cutoff+2:]
        f.write("<remove_single> : <returning results> \n")
        return result

def remove_multi(destination, result):
    '''Removes one multi property from a string (skips over "()"s and ","s), 
    returns the string, and appends the removed value to the destination 
    (as a list)
    '''
    f.write("<remove_multi> : <expects a destination and result. appends to destination and cuts off result.> \n")

    #Handles empty returns
    if result == "":
        return 

    if (result[0] == " "):
        result = result[1:]
    temp_list = []
    for index in range(0, len(result)):
        if (result[index] == "("):
            result = result[2:]
            end_index = result.rfind(")")
            counter = 0
            for char in range (0, len(result)):
                if (result[char] == ","):
                    if (result[char-8:char-3] == "TIME|"):
                        continue
                    elif (result[char+1] == " "):
                        temp_list.append(result[counter:char])
                        counter = char + 2
                    else:
                        temp_list.append(result[counter:char])
                        counter = char + 1
                elif(char == end_index):
                    temp_list.append(result[counter:char-1])
                    break
                else:
                        continue
            result = result[end_index+3:]
            destination.append(temp_list)
            f.write("<remove_multi> : <returning result> \n")
            return result
        else:
            return remove_single(destination, result)



#returnTypes returns the property types, in order of properties (in terms of Single/Multiple)
#   SINGLE: only returns one value per line (examples: IP Address, Computer Name)
#   MULTIPLE: returns multiple values per line as comma separated values (examples: MAC Addresses)
# Single/Multiple rules: 
#       -Multiple values can appear single in some instances, if only one value is returned (example: if a computer only has one MAC address)
#       -Actual multiple values are comma separated and between parenthesis: (value1, value2, value3)
#       -Single values are always comma separated:   value1,

def return_types(result, property_numbers):
    return_list = []
    '''#return_types returns the property types, in order of properties (in terms of Single/Multiple)
    SINGLE: only returns one value per line (examples: IP Address, Computer Name)
     MULTIPLE: returns multiple values per line as comma separated values (examples: MAC Addresses)
    Single/Multiple rules: 
       -Multiple values can appear single in some instances, if only one value is returned (example: if a computer only has one MAC address)
       -Actual multiple values are comma separated and between parenthesis: (value1, value2, value3)
       -Single values are always comma separated:   value1,'''

    f.write("<return_types> : <expecting results and property_numbers to decipher singles vs multiples> \n")
    daynames = ["mon", "tue", "wed", "thur", "fri", "sat", "sun"]

    for size in range(0, len(result)):
        #Keeps count of which property is being tested.
        index = 0 
        char = 0
        while (char < len(result[size])):
            #If you hit a comma first, the result is single (for now)
            if (result[size][char] == ","):   
                #Tests if this is the first run through (list must be appended)
                if (len(return_list) < property_numbers):
                    return_list.append("S") 
                char += 1
                index += 1
                     
            #If you hit a parenthesis first, the result is definitely multiple
            elif (result[size][char] == "("):   
                endindex = result[size][char:].find(")")
                if (endindex != -1):
                    if ((len(return_list) < property_numbers) and (result[size][char:endindex].find(",") != -1)):
                        return_list.append("M")                                            
                    else:

                        #Exception. This could possibly pick up (None) markers hidden in certain Properties. This does not make them multiple properties.
                        #if (result[size][(char+2):(char+8)] == "(None)"):
                        #    char = char+10
                        #    break

                        #Exception: This is a single property, with a value including "(" and ")"
                        if (result[size][char:endindex].find(",") == -1):
                            break
                        #It is possible the value came up as singular previously, and was incorrectly marked as a single property
                        if (return_list[index] == "S"): 
                            return_list[index] = "M"  
                temp_result = ""
                for each in range(char, len(result[size])):
                    #At this point we must skip over all commas inside the parenthesis, so we search for ")" and iterate past it
                    temp_result = temp_result + result[size][each] 
                char = char + temp_result.index(")") + 2
                index += 1
                    
            elif (char == len(result[size]) - 1):
                #At the end, there is no ",". If we didn't end on a ")" and iterate out of the loop, this last value is singular
                if (len(return_list) < property_numbers):  
                    return_list.append("S")
                char += 1  
                                   
            else:
                char += 1

    f.write("<return_types> : <returning return_list (types)> \n")
    return return_list


def Single(result):
    '''Saves a result with only one property that is a single'''
    f.write("<Single> : <expects result to pull single property from> \n")
    tempAll = []
    for each in range (0, len(result)):
        temp = []
        temp.append(result[each])
        tempAll.append(temp)
    f.write("<Single> : <returning tempAll (list of results)> \n")
    return tempAll

def Multiple(result):
    '''Saves a result with only one property that is a multiple'''
    f.write("<Multiple> : <expects a result to pull multiple properties from> \n")
    Property1 = []
    Property1temp = []
    for index in range(0, len(result)):
        counter = 0
        char = 0
        while (char < len(result[index])):
            if (result[index][char] == ","):
                if (result[index][char-8:char-3] == "TIME|"):
                        char = char + 1
                        continue
                else:
                    Property1temp.append(result[index][counter:char])
                    counter = char+1
            elif (char == len(result[index])-1):
                Property1temp.append(result[index][counter:])
            char = char + 1   
        Property1.append(list(Property1temp))
        while (len(Property1temp) != 0):
            Property1temp.pop()
    f.write("<Multiple> : <returning Property1 (list of properties> \n")
    return Property1

f.write("START OF QUERY_CREATOR PROGRAM. \n")

##***********************************EXAMPLES************************************##

#results = ["Computer Name", "MAC Addresses"]
#filters = ["Computer Name", "starts with", "iso-", "OR", "a"]
#search = "computers"
#myQuery = relevance_query(results, filters, search)

#username = "FakeUsername"
#password = "FakePassword"
#website = "FakeURL.com"
#myResult = soap_query(username, password, website, myQuery.Query)

#myObject = create(myQuery, myResult)

#OR

#myQuery = input_query()
#myResult = input_soap(myQuery.Query)
#myObject = create(myQuery, myResult)
#myObject.print_index()


#WORKING EXAMPLE!!!!
# just load your username and password in to this = )

'''
filter_line_1 = ["OS", "contains", "Win"]

filter_line_2 = ["OS", "does not contain", "XP", "and", "2003", "and", "2008", "and", "2012"]

filter_line_3 = ["EMET Service Version ([STANFORD] Microsoft Enhanced Mitigation Experience Toolkit Information (EMET))", "contains", "5.", "or", "4.", "or", "3."]

filter_line_4 = ["EMET Service Channel ([STANFORD] Microsoft Enhanced Mitigation Experience Toolkit Information (EMET))", "is", "alpha", "or", "beta", "or", "production"]

master_filter = [filter_line_1, filter_line_2, filter_line_3, filter_line_4]

returned_columns = ["EMET Auto_Backdown Simple Health Check"]

username = "fakeusername"
password = "fakepassword"
website = "https://bfreports.stanford.edu"

MyQuery = relevance_query(returned_columns, master_filter, "computers")

MyResults = soap_query(username, password, website, MyQuery.Query)

MyObject = create(MyQuery, MyResults)

MyObject.print_index()
'''
