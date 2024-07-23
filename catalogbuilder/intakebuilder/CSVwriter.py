import os.path
import csv
from csv import writer
from intakebuilder import builderconfig, configparser 

def getHeader(configyaml):
    '''
    returns header that is the first line in the csv file, refers builderconfig.py
    :return: headerlist with all columns
    '''
    if configyaml:
        return configyaml.headerlist
    else:
        return builderconfig.headerlist

def writeHeader(csvfile):
  '''
  writing header for the csv
  :param csvfile: pass csvfile absolute path
  :return: csv writer object
  '''
  # list containing header values
  # inputting these headers into a csv
  with open(csvfile, "w+", newline="") as f:
        writerobject = csv.writer(f)
        writerobject.writerow(builderconfig.headerlist)

def file_appender(dictinputs, csvfile):
    '''
    creating function that puts values in dictionary into the csv
    :param dictinputs:
    :param csvfile:
    :return:
    '''
    # opening file in append mode
    with open(csvfile, 'a', newline='') as write_obj:
        # Create a writer object from csv module
        csv_writer = writer(write_obj)
        # add contents of list as last row in the csv file
        csv_writer.writerow(dictinputs)

def listdict_to_csv(dict_info,headerlist, csvfile, overwrite, append):
    try:
        #Open the CSV file in write mode and add any data with atleast 3 values associated with it
        if overwrite:
            with open(csvfile, 'w') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=headerlist)
                print("writing..")
                writer.writeheader()
                for data in dict_info:
                    if len(data.keys()) > 2:
                        writer.writerow(data)
        #Open the CSV file in append mode and add any data with atleast 3 values associated with it
        if append:
            with open(csvfile, 'a') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=headerlist)
                print("writing (without header)..")
                for data in dict_info:
                    if len(data.keys()) > 2:
                        writer.writerow(data)
        #If neither overwrite nor append flags are found, check if a csv file already exists. If so, prompt user on what to do. If not, write to the file. 
        if not any((overwrite, append)):
            if os.path.isfile(csvfile):
                user_input = ''
                while True:
                    user_input = input('Found existing file! Overwrite? (y/n)')

                    if user_input.lower() == 'y':
                        with open(csvfile, 'w') as csvfile:
                            writer = csv.DictWriter(csvfile, fieldnames=headerlist)
                            print("writing..")
                            writer.writeheader()
                            for data in dict_info:
                                if len(data.keys()) > 2:
                                    writer.writerow(data)
                        break
                    
                    elif user_input.lower() == 'n':
                        with open(csvfile, 'a') as csvfile:
                            writer = csv.DictWriter(csvfile, fieldnames=headerlist)
                            print("appending (without header) to existing file...")
                            for data in dict_info:
                                if len(data.keys()) > 2:
                                    writer.writerow(data)
                        break
                    #If the user types anything besides y/n, keep asking
                    else:
                        print('Type y/n')
            else:
                with open(csvfile, 'w') as csvfile:
                    writer = csv.DictWriter(csvfile, fieldnames=headerlist)
                    print("writing..")
                    writer.writeheader()
                    for data in dict_info:
                        if len(data.keys()) > 2:
                            writer.writerow(data)
    except IOError:
        print("I/O error")
