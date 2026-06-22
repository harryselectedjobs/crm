from aws_connection.dynamodb_connection import _get_dynamodb_client
from repository.db_connection import get_db_connection
from boto3.dynamodb.conditions import Attr
from boto3.dynamodb.conditions import Key


def check_email_id_exits_in_contact(input_email: str) -> bool:
    conn = get_db_connection()
    if not conn:
        return False

    try:
        cursor = conn.cursor()

        query = """
        SELECT 1
        FROM contacts
        WHERE email = %s
        LIMIT 1
        """

        cursor.execute(query, (input_email,))

        return cursor.fetchone() is not None

    finally:
        cursor.close()
        conn.close()


def delete_sequence_enrollment_by_email(email: str) -> int:
    dynamodb = _get_dynamodb_client()
    table = dynamodb.Table("SequenceEnrollments")

    deleted_count = 0

    response = table.scan(
        FilterExpression=Attr("email").eq(email)
    )

    while True:
        items = response.get("Items", [])

        for item in items:
            table.delete_item(
                Key={
                    "sequence_id": item["sequence_id"],
                    "enrollment_id": item["enrollment_id"]
                }
            )
            deleted_count += 1

        if "LastEvaluatedKey" not in response:
            break

        response = table.scan(
            FilterExpression=Attr("email").eq(email),
            ExclusiveStartKey=response["LastEvaluatedKey"]
        )

    return deleted_count


def save_lead_from_sequence(
    name: str,
    email: str,
    company_name: str,
    status: str = "open"
):
    TABLE_NAME = "CRMSequenceLeads"

    if status not in {"open", "closed"}:
        raise ValueError("status must be either 'open' or 'closed'")

    table = _get_dynamodb_client().Table(TABLE_NAME)

    table.put_item(
        Item={
            "email": email,
            "name": name,
            "company_name": company_name,
            "status": status,
        }
    )

    return {"message": "Lead saved successfully"}


def get_leads_by_status(status: str):
    TABLE_NAME = "CRMSequenceLeads"

    if status not in ("open", "closed"):
        raise ValueError("status must be open or closed")

    table = _get_dynamodb_client().Table(TABLE_NAME)

    items = []

    response = table.query(
        IndexName="status-index",
        KeyConditionExpression=Key("status").eq(status)
    )

    items.extend(response.get("Items", []))

    while "LastEvaluatedKey" in response:
        response = table.query(
            IndexName="status-index",
            KeyConditionExpression=Key("status").eq(status),
            ExclusiveStartKey=response["LastEvaluatedKey"]
        )

        items.extend(response.get("Items", []))

    return items


def update_lead_status(email: str, status: str):
    TABLE_NAME = "CRMSequenceLeads"

    if status not in ("open", "closed"):
        raise ValueError("status must be open or closed")

    table = _get_dynamodb_client().Table(TABLE_NAME)

    response = table.update_item(
        Key={
            "email": email
        },
        UpdateExpression="SET #s = :status",
        ExpressionAttributeNames={
            "#s": "status"
        },
        ExpressionAttributeValues={
            ":status": status
        },
        ConditionExpression="attribute_exists(email)",
        ReturnValues="ALL_NEW"
    )

    return response["Attributes"]

