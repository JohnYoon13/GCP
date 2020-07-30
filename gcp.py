#STAGE 1
#imports the pub/sub package needed for pull request
from google.cloud import pubsub_v1
#project name
PROJECT = ["PROJECT NAME HERE"]
#subscription name
path = "demo-subscription"
#creates the subscriber client that will access the subscription
subscriber = pubsub_v1.SubscriberClient()
subscription_path = subscriber.subscription_path(PROJECT, path)
#subscriber pulls data from the subscription and stores the response
response = subscriber.pull(subscription_path, max_messages=1)
#collect and acknowledge all ack_ids
ack_ids = [received_message.ack_id for received_message in response.received_messages]
#subscriber.acknowledge(subscription_path, ack_ids)


#STAGE 2
#creates a list to collect responses
responses = [received_message.message.data.decode('utf-8') for received_message in response.received_messages]
#shows the first response
print(responses[0])
#capitalizes all letters, and multiplies all integers by 10
word, number = responses[0].split(' ')
transformed_word = word.upper()
transformed_number = ''.join(str(int(x) * 10) for x in number)
#appends all the modified data in a combined format into a new list
new_answer = []
new_answer.append(f'{transformed_word} {transformed_number}')


#STAGE 3
#imports the bigquery package needed for table insertion
from google.cloud import bigquery
#creates the bigquery client that will access the dataset and table
bigquery_client = bigquery.Client(project=PROJECT)
#sets up access for the specified data set
dataset_ref = bigquery_client.dataset("demo")
#sets up access for the specified table
table_ref = dataset_ref.table("demo_result")
table = bigquery_client.get_table(table_ref)
#the data that will be sent to the table
data_to_insert = new_answer[0]
#inserts the data into the table 
errors = bigquery_client.insert_rows(table, [(responses[0], data_to_insert)])
if not errors:
  print("New rows added.")