import boto3, json

ecs = boto3.client('ecs')

def get_latest_task_definition_arn(family):
    response = ecs.list_task_definitions(familyPrefix=family, sort='DESC')
    if len(response['taskDefinitionArns']) == 0:
        return None
    latest_revision = response['taskDefinitionArns'][0]
    
    return latest_revision

def register_revision(latest_revision, image, tag):
    task_definition = ecs.describe_task_definition(taskDefinition=latest_revision)
    task_definition['taskDefinition']['containerDefinitions'][0]['image'] = f"{image}:{tag}"
    ecs.register_task_definition(family=task_definition['taskDefinition']['family'],containerDefinitions=task_definition['taskDefinition']['containerDefinitions'])
    return True

def update_ecs_service(cluster, service, image, tag):
    family = get_task_families(cluster=cluster, service=service)
    latest_revision = get_latest_task_definition_arn(family=family)
    if latest_revision is None: return None

    register_revision(latest_revision, image, tag)

    new_revision = get_latest_task_definition_arn(family=family)

    response = ecs.update_service(
        cluster=cluster,
        service=service,
        taskDefinition=new_revision,
    )

    return response

def get_task_families(cluster, service):
    response = ecs.describe_services(
        cluster=cluster,
        services=[service]
    )

    if 'services' in response and len(response['services']) > 0:
        service = response['services'][0]
        task_definition_arns = service.get('deployments', [])[0].get('taskDefinition')
        if isinstance(task_definition_arns, str):
            return task_definition_arns.split('/')[1].split(':')[0]
        elif isinstance(task_definition_arns, list):
            family_list = []
            for arn in task_definition_arns:
                family = arn.split('/')[1].split(':')[0]
                family_list.append(family)
            return family_list
        else:
            return []
    else:
        return []