import json
from datetime import datetime, timezone

from aws_connection.dynamodb_connection import _get_dynamodb_client
from news_tab.guardianAPI import fetch_guardian_technology_news

TABLE_NAME = "tech_news_cache"


# ─────────────────────────────────────────
#  Create table (run once)
# ─────────────────────────────────────────

def create_table():
    dynamodb = _get_dynamodb_client()

    existing = [t.name for t in dynamodb.tables.all()]
    if TABLE_NAME in existing:
        print(f"Table '{TABLE_NAME}' already exists. Skipping creation.")
        return dynamodb.Table(TABLE_NAME)

    table = dynamodb.create_table(
        TableName=TABLE_NAME,
        KeySchema=[
            {"AttributeName": "date", "KeyType": "HASH"},   # Partition key
        ],
        AttributeDefinitions=[
            {"AttributeName": "date", "AttributeType": "S"},
        ],
        BillingMode="PAY_PER_REQUEST",   # No need to set read/write capacity
    )

    table.wait_until_exists()
    print(f"Table '{TABLE_NAME}' created successfully.")
    return table


# ─────────────────────────────────────────
#  Check if news exists for a date
# ─────────────────────────────────────────

def news_exists_for_date(date: str) -> bool:
    dynamodb = _get_dynamodb_client()
    table = dynamodb.Table(TABLE_NAME)

    response = table.get_item(Key={"date": date})
    return "Item" in response


# ─────────────────────────────────────────
#  Save news for a date
# ─────────────────────────────────────────

def save_news(date: str, articles: list) -> dict:
    dynamodb = _get_dynamodb_client()
    table = dynamodb.Table(TABLE_NAME)

    item = {
        "date": date,
        "articles": json.dumps(articles),           # Store as JSON string (DynamoDB safe)
        "article_count": len(articles),
        "saved_at": datetime.now(timezone.utc).isoformat(),
    }

    table.put_item(Item=item)
    print(f"Saved {len(articles)} articles for date: {date}")
    return item


# ─────────────────────────────────────────
#  Get news for a date
# ─────────────────────────────────────────

def get_news_by_date(date: str) -> list | None:
    dynamodb = _get_dynamodb_client()
    table = dynamodb.Table(TABLE_NAME)

    response = table.get_item(Key={"date": date})

    if "Item" not in response:
        print(f"No news found for date: {date}")
        return None

    item = response["Item"]
    articles = json.loads(item["articles"])
    print(f"Retrieved {len(articles)} articles for date: {date}")
    return articles

def fetch_and_save_the_news(date):
    if news_exists_for_date(date):
        print(f"Cache hit: returning existing news for {date}")
        return get_news_by_date(date)

    print(f"Cache miss: fetching news for {date}")
    response = fetch_guardian_technology_news()
    articles = response.get("response", {}).get("results", [])
    save_news(date, articles)
    return articles

# create_table()

