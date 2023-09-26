# ECS service update POC

Here is a portion of POC for updating an image and tag for a ECS service using Lambda function.

## How it works

### Lambda function

Lambda function is written in Python as it was mentioned in the README file. Another reason that I have experince with Python.

Lambda function consists of the following functions in the logical order:
1. update_ecs_service - main function, that takes cluster, service, image, tag to update the target ECS service
2. get_task_families - the function, that takes cluster and service and return a family for the task. For simplicity and to finish the task in time I use one family.
3. get_latest_task_definition_arn - the function, that takes task family to retrieve the latest task definition
4. register_revision - the function, that takes latest_revision, as object from get_latest_task_definition_arn, image name and image tag to update the image and tag in the latest revision and register it as a new one
5. get_latest_task_definition_arn - the function, that takes family as input to retrieve the last revision, but now it's the one, we have created on step 4
6. on this step we use ecs built-in function update_service and provide cluster, service and new task definition to update existing service

In response I return the description of the new task definition.

>Improvements:  
> - For each function should be add more check to cover corner cases.
> - The final response can be more precise depends on what's required. I would go with the time creation, service name, status

### Trigger solution instructions

Gather the details:
- Go to solution output and take the ApiInvokeUrl.
- Go to solution output, click on ECSUpdateApiKey value link, in the API key line click on show and copy the API key.
Go to workload output and take cluster name and service name.

Update the following request with the above mentioned details:

``` bash
curl -X POST \
 -H "x-api-key: <API_KEY>" \
 -H "Content-Type: application/json" -d '{
  "cluster": "<CLUSTER_NAME>",
  "service": "<SERVICE_NAME>",
  "image": "<IMAGE_NAME>",
  "tag": "<IMAGE_TAG>"
}' "<API_INVOKE_URL>"
```  

>Improvements:  
> - Gather all the necessary details using Lambda functions and write them in the files  
> OR
> - Use declarative way to provide the details for the ECS, which is way better as in this case we use GitOps approach and can switch between versions of ECS Service description file
> - Use Code Pipeline to triger the API request

### Cloud Formation Templates

For the solution I used Cloud Formation templates to faciliate deploying the resources and have all AWS-based.

There are couple of crucial resources that make solution work:
1. Lambda related
   1. Lambda function
   2. Lambda role, allows Lambda function do anything with ECS
2. API gateway related
   1. REST API
   2. API "update" resource
   3. API "update" endpoint (method)
   4. API gateway model for mapping payload
   5. API gateway deployment, stage, usage plan, usage plan key
   6. API gateway API key
   7. API gateway Lambda execution role, allows to invoke Lambda function
3. ECS workload (for test purpose)
   1. ECS Service
   2. ECS task definition

>Improvements:  
> - Maybe something can be improved or removed or additional details can be specified