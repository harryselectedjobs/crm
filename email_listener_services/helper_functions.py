from aws_connection.dynamodb_connection import _get_dynamodb_client
from repository.db_connection import get_db_connection
from boto3.dynamodb.conditions import Attr


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




