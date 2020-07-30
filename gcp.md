# **Introduction**

## Goals
This tutorial focuses on two goals:
*   Showing new users how to interact with Google Cloud Platform's Pub/Sub & BigQuery.
*   Serving as a refresher for experienced Google Cloud Platform users.


## The Approach

These goals will be achieved by exploring a practical and common use case implemented in Python that includes three primary stages: 

1.  Extracting data from a Pub/Sub subscription.
2.  Minimally transforming the data.
3.  Sending the data to a BigQuery table.

![](https://github.com/JohnYoon13/GCP/blob/master/images/image0.png) 


# **Prerequisites**

## Permissions
Prior to any implementation, first verify that the necessary [permissions](https://cloud.google.com/iam/docs/permissions-reference) and [roles](https://cloud.google.com/iam/docs/understanding-roles) for the project are established. This can range from topics and subscriptions, to BigQuery, to whichever service holds and runs the source code, i.e., cloud functions.

***Note: This process may require coordination with project owners and administrators

## Topics & Subscriptions
In following with the [Pub/Sub](https://cloud.google.com/pubsub/architecture) paradigm, a pipeline consisting of a [topic](https://cloud.google.com/pubsub/docs/admin#managing_topics) and corresponding [subscription](https://cloud.google.com/pubsub/docs/admin#manage_subs) must possess data flowing through it. 

![](https://github.com/JohnYoon13/GCP/blob/master/images/image1.png) 

For the purposes of this guide, a sample topic labeled, __demo-topic__, and a sample subscription labeled, __demo-subscription__, have been created. Using [cloudscheduler](https://cloud.google.com/scheduler/docs/quickstart), a string (named __test 123__) is sent to __demo-topic__ every 10 minutes. This is the data that will later undergo a transformation and ship out to the BigQuery table.

## BigQuery Table
After minor modifications, the sample string will enter a [BigQuery](https://cloud.google.com/bigquery/docs/quickstarts/quickstart-web-ui) table. Therefore, this workflow requires a table that can receive the incoming data. For this demonstration, a table (named __demo_results__) already exists with two fields: 
* "Original," which holds string data type. 
* "Modified," which holds string data type.


# **Stage 1: Extracting data from the subscription**

### Import the Pub/Sub [package](https://cloud.google.com/pubsub/docs/reference/service_apis_overview).
```python
#imports the pub/sub package needed for pull request
from google.cloud import pubsub_v1
```
### Define the variable names for the project and the subscription path.
```python
#project name
PROJECT = ["PROJECT NAME HERE"]
#subscription name
path = "demo-subscription"
```

### Generate a [subscriber client](https://googleapis.dev/python/pubsub/latest/subscriber/api/client.html) that corresponds with the subscription.
```python
#creates the subscriber client that will access the subscription
subscriber = pubsub_v1.SubscriberClient()
subscription_path = subscriber.subscription_path(PROJECT, path)
```

### Call the subscriber client's pull method to get a response. Then show the results.
```python
#subscriber pulls data from the subscription and stores the response
response = subscriber.pull(subscription_path, max_messages=1)
#displays the pulled results
print(response)
```

### The results should include the expected data (__test 123__), as well as the ack_id, message_id, and publish_time. 
```javascript

received_messages {
  ack_id: "ABC-DEFG"
  message {
    data: "test 123"
    message_id: "1234567"
    publish_time {
      seconds: 1595878800
      nanos: 501000000
      }}}
```


### Tie up loose ends by collecting the acknowledgment IDs of all pulled messages and acknowledging them. 
```python
#collect and acknowledge all ack_ids
ack_ids = [received_message.ack_id for received_message in response.received_messages]
subscriber.acknowledge(subscription_path, ack_ids)
```

# **Stage 2: Manipulate the pulled data**

### Gather all the pulled data and display the first element of the results. In this instance, since there is only one pulled case (__test 123__), the first element will be the entire data set. 
```python
#creates a list to collect responses
responses = [received_message.message.data.decode('utf-8') for received_message in response.received_messages]
#shows the first response
print(responses[0])

```
### Modify the data by transforming all lower case letters into upper case, and by multiplying all integers by ten.
```python
#capitalizes all letters, and multiplies all integers by 10
word, number = responses[0].split(' ')
transformed_word = word.upper()
transformed_number = ''.join(str(int(x) * 10) for x in number)
```

### Concatenate all the modified data parts, and append it to the new answer list. Display the final manipulated data results, which should show, __TEST 102030__.
```python
#appends all the modified data in a combined format into a new list
new_answer = []
new_answer.append(f'{transformed_word} {transformed_number}')
#shows the new answer
print(new_answer)
```

# **Stage 3: Inserting the results into a BigQuery table**

### Import the [BigQuery](https://googleapis.dev/python/bigquery/latest/generated/google.cloud.bigquery.client.Client.html) package. Then setup the client, which will access the project.
```python
#imports the bigquery package needed for table insertion
from google.cloud import bigquery
#creates the bigquery client that will access the dataset and table
bigquery_client = bigquery.Client(project=PROJECT)
```

### Specify the data set and table (which should already be set up, per the **Prerequisites** section of the tutorial).
```python
#sets up access for the specified data set
dataset_ref = bigquery_client.dataset("demo")
#sets up access for the specified table
table_ref = dataset_ref.table("demo_result")
table = bigquery_client.get_table(table_ref)
```

### Get the data that will be sent to BigQuery. Then insert the data on a row-to-row basis using the **insert_rows** [function](https://googleapis.dev/python/bigquery/latest/generated/google.cloud.bigquery.client.Client.html). If no errors arise, then the display will show "New rows added."
```python
#the data that will be sent to the table
data_to_insert = new_answer[0]
#inserts the data into the table 
errors = bigquery_client.insert_rows(table, [(responses[0], data_to_insert)])
if not errors:
  print("New rows added.")
```

### The end result shown in the table should look like the following:

![](https://github.com/JohnYoon13/GCP/blob/master/images/image2.png) 

# Conclusion
## In this tutorial we have demonstrated how to:
1. Acquire data from a Pub/Sub Subscriptions.
2. Pythonically modify the aforementioned data.
3. Insert the modified data into a BigQuery table.

## The complete code can be found [here](https://github.com/JohnYoon13/GCP/blob/master/gcp.py).





