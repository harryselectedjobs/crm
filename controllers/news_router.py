from fastapi import APIRouter, HTTPException
from news_tab.news_tab_services import fetch_and_save_the_news

router = APIRouter(prefix="/tech-news", tags=["Tech News"])


@router.get("/{date}")
def get_tech_news(date: str):
    try:
        articles = fetch_and_save_the_news(date)
        return {
            "date": date,
            "article_count": len(articles),
            "articles": articles,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))