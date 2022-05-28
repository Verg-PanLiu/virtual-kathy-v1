import boto3
import csv

# this script is to upload local data to cloud database service (AWS DynamoDB)

#######################################################################
#######################################################################
# PLEASE REPLACE aws_access_key_id AND aws_secret_access_key WITH YOUR OWN
# ACCESS KEY OF Amazon Web Services (AWS) TO ACCESS DynamoDB. YOU MAY ALSO
# HAVE DIFFERENT TABLE NAMES,FEEL FREE TO MODIFY
dyndb = boto3.resource('dynamodb',
                       region_name='YOUR SERVICE REGION',
                       aws_access_key_id='YOUR ACCESS KEY ID',
                       aws_secret_access_key='YOUR SECRET ACCESS KEY')

table1 = dyndb.Table("Pitt_CS_Courses")
table2 = dyndb.Table("Pitt_CS_Faculty")
table3 = dyndb.Table("Courses_Schedule")
table4 = dyndb.Table("Add_Questions")
table5 = dyndb.Table("Question_list")

#######################################################################
#######################################################################

# Reading the csv file, uploading the blobs and creating the table
with open('./Pitt_CS_Courses.csv', 'r') as csvfile:
    csvf = csv.reader(csvfile, quotechar='"')
    next(csvf)
    for item in csvf:
        # print(item)
        metadata_item = {'Course ID': item[1],
                         'Course Name': item[2],
                         'Course Credits': item[3],
                         'Course Component': item[4],
                         'Grade Component': item[5],
                         'Course Requirements': item[6],
                         'Academic Career': item[7],
                         'Description': item[8]
                         }
        try:
            table1.put_item(Item=metadata_item)
        except:
            print("item may already be there or another failure")


# Reading the csv file, uploading the blobs and creating the table
with open('./Pitt_CS_Faculty.csv', 'r') as csvfile:
    csvf = csv.reader(csvfile, quotechar='"')
    next(csvf)
    for item in csvf:
        #print(item)
        metadata_item = {'Full Name': item[1],
                         'First Name': item[2],
                         'Last Name': item[3],
                         'Email Address': item[4],
                         'Phone Number': item[5],
                         'Position': item[6],
                         'Profile': item[7]
                         }
        try:
            table2.put_item(Item=metadata_item)
        except:
            print("item may already be there or another failure")


# Reading the csv file, uploading the blobs and creating the table
with open('./Courses_Schedule.csv', 'r') as csvfile:
    csvf = csv.reader(csvfile, quotechar='"')
    next(csvf)
    for item in csvf:
        #print(item)
        metadata_item = {'Subject Code': item[0],
                         'Course Number': item[1],
                         'Class Number': item[2],
                         'Associated Class Number': item[3],
                         'Days': item[4],
                         'Start Time': item[5],
                         'End Time': item[6],
                         'Room': item[7],
                         'Instructor(s)': item[8],
                         'instructor_pittid': item[9],
                         'Ta(s)': item[10],
                         'Type': item[11],
                         'Session': item[12],
                         'Writing': item[13],
                         'Enrollment Cap': item[14],
                         'Current Enrollment': item[15],
                         'Current Waitlist': item[16],
                         'cross_list_id': item[17],
                         'Notes': item[18],
                         'Description': item[19],
                         'deleted': item[20],
                         'Academic Term Code': item[21],
                         'last_modified': item[22]
                         }
        try:
            table3.put_item(Item=metadata_item)
        except:
            print("item may already be there or another failure")

# Reading the csv file, uploading the blobs and creating the table
with open('./questions.csv', 'r') as csvfile:
    csvf = csv.reader(csvfile, quotechar='"')
    next(csvf)
    for item in csvf:
        metadata_item = {'Category': item[0],
                         'Question ID': item[1],
                         'Question': item[2],
                         'Answer': item[4],
                         }
        try:
            table5.put_item(Item=metadata_item)
        except:
            print("item may already be there or another failure")











