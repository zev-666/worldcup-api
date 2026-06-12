"""
World Cup 2026 LangGraph Data Agent
執行方式：python scripts/run_agent.py --task scrape_daily
"""
import argparse
import asyncio
import logging
import os
from datetime import date
from typing import TypedDict, List

from langgraph.graph import StateGraph, END
import httpx

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)


class AgentState(TypedDict):
    task: str
    date: str
    matches_to_scrape: List[dict]
    scraped_odds: List[dict]
    scraped_squads: List[dict]
    errors: List[str]
    written_count: int


async def plan_node(state: AgentState) -> AgentState:
    logger.info(f"[Plan] 取得 {state['date']} 比賽清單")

    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.get(
            f"{os.environ['SUPABASE_URL']}/rest/v1/matches",
            headers={
                "apikey": os.environ["SUPABASE_KEY"],
                "Authorization": f"Bearer {os.environ['SUPABASE_KEY']}",
            },
    url = (
        f"{os.environ['SUPABASE_URL']}/rest/v1/matches"
        f"?select=id,home_team,away_team,kickoff_utc"
        f"&kickoff_utc=gte.{state['date']}T00:00:00Z"
        f"&kickoff_utc=lte.{state['date']}T23:59:59Z"
    )

    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.get(
            url,
            headers={
                "apikey": os.environ["SUPABASE_KEY"],
                "Authorization": f"Bearer {os.environ['SUPABASE_KEY']}",
            }
        )
        )

    if resp.status_code == 200:
        matches = resp.json()
    else:
        logger.error(f"[Plan] 查詢失敗: {resp.status_code} {resp.text}")
        matches = []

    logger.info(f"[Plan] 找到 {len(matches)} 場比賽")
    return {**state, "matches_to_scrape": matches}


async def scrape_odds_node(state: AgentState) -> AgentState:
    logger.info(f"[Odds] 開始抓取賠率（{len(state['matches_to_scrape'])} 場）")
    scraped_odds = []
    errors = list(state.get("errors", []))

    async with httpx.AsyncClient(timeout=30) as client:
        for match in state["matches_to_scrape"]:
            try:
                resp = await client.get(
                    "https://api.oddspapi.com/v1/odds",
                    params={
                        "apiKey": os.environ.get("ODDSPAPI_KEY", ""),
                        "sport": "soccer",
                        "league": "FIFA World Cup",
                    }
                )
                raw = resp.json() if resp.status_code == 200 else {"status": "no_data"}
                scraped_odds.append({
                    "match_id": match["id"],
                    "home_team": match["home_team"],
                    "away_team": match["away_team"],
                    "raw_data": raw,
                    "scraped_at": date.today().isoformat()
                })
                await asyncio.sleep(1)

            except Exception as e:
                msg = f"賠率抓取失敗 {match.get('home_team')} vs {match.get('away_team')}: {e}"
                logger.warning(msg)
                errors.append(msg)

    logger.info(f"[Odds] 完成 {len(scraped_odds)} 筆")
    return {**state, "scraped_odds": scraped_odds, "errors": errors}


async def scrape_squads_node(state: AgentState) -> AgentState:
    logger.info("[Squads] 開始抓取球隊陣容")
    scraped_squads = []
    errors = list(state.get("errors", []))

    async with httpx.AsyncClient(timeout=30) as client:
        for match in state["matches_to_scrape"]:
            try:
                resp = await client.get(
                    "https://api.football-data.org/v4/competitions/WC/teams",
                    headers={
                        "X-Auth-Token": os.environ.get("FOOTBALL_API_KEY", "")
                    }
                )
                if resp.status_code == 200:
                    scraped_squads.append({
                        "match_id": match["id"],
                        "home_team": match["home_team"],
                        "away_team": match["away_team"],
                        "teams_data": resp.json(),
                        "scraped_at": date.today().isoformat()
                    })
                else:
                    logger.warning(f"陣容 API 回傳 {resp.status_code}，略過")
                await asyncio.sleep(1)

            except Exception as e:
                msg = f"陣容抓取失敗 {match.get('home_team')}: {e}"
                logger.warning(msg)
                errors.append(msg)

    logger.info(f"[Squads] 完成 {len(scraped_squads)} 筆")
    return {**state, "scraped_squads": scraped_squads, "errors": errors}


async def write_node(state: AgentState) -> AgentState:
    logger.info("[Write] 開始寫入 Supabase")
    written_count = 0
    errors = list(state.get("errors", []))

    async with httpx.AsyncClient(timeout=30) as client:
        headers = {
            "Authorization": f"Bearer {os.environ['INTERNAL_API_TOKEN']}",
            "Content-Type": "application/json"
        }
        endpoint = f"{os.environ['API_ENDPOINT']}/api/scraped-data/accept"

        for odds_data in state.get("scraped_odds", []):
            try:
                resp = await client.post(endpoint, headers=headers, json={
                    "data_type": "odds",
                    "match_id": odds_data["match_id"],
                    "content": odds_data,
                    "date": state["date"]
                })
                if resp.status_code in (200, 201):
                    written_count += 1
                    logger.info(f"寫入 odds 成功: {odds_data['home_team']} vs {odds_data['away_team']}")
                else:
                    errors.append(f"寫入 odds 失敗: {resp.status_code} {resp.text}")
            except Exception as e:
                errors.append(f"寫入異常: {e}")

        for squad_data in state.get("scraped_squads", []):
            try:
                resp = await client.post(endpoint, headers=headers, json={
                    "data_type": "squads",
                    "match_id": squad_data["match_id"],
                    "content": squad_data,
                    "date": state["date"]
                })
                if resp.status_code in (200, 201):
                    written_count += 1
                    logger.info(f"寫入 squads 成功: {squad_data['home_team']}")
                else:
                    errors.append(f"寫入 squads 失敗: {resp.status_code} {resp.text}")
            except Exception as e:
                errors.append(f"寫入異常: {e}")

    logger.info(f"[Write] 成功寫入 {written_count} 筆，錯誤 {len(errors)} 筆")
    return {**state, "written_count": written_count, "errors": errors}


def should_continue(state: AgentState) -> str:
    if not state.get("matches_to_scrape"):
        logger.info("[Router] 今日無比賽，流程結束")
        return "end"
    return "scrape_odds"


def build_graph():
    graph = StateGraph(AgentState)
    graph.add_node("plan", plan_node)
    graph.add_node("scrape_odds", scrape_odds_node)
    graph.add_node("scrape_squads", scrape_squads_node)
    graph.add_node("write", write_node)
    graph.set_entry_point("plan")
    graph.add_conditional_edges(
        "plan",
        should_continue,
        {"scrape_odds": "scrape_odds", "end": END}
    )
    graph.add_edge("scrape_odds", "scrape_squads")
    graph.add_edge("scrape_squads", "write")
    graph.add_edge("write", END)
    return graph.compile()


async def main():
    parser = argparse.ArgumentParser(description="World Cup 2026 LangGraph Agent")
    parser.add_argument("--task", default="scrape_daily",
                        choices=["scrape_daily", "test"])
    parser.add_argument("--date", default=date.today().isoformat())
    args = parser.parse_args()

    logger.info(f"Agent 啟動：task={args.task}, date={args.date}")

    initial_state = AgentState(
        task=args.task,
        date=args.date,
        matches_to_scrape=[],
        scraped_odds=[],
        scraped_squads=[],
        errors=[],
        written_count=0
    )

    app = build_graph()
    final_state = await app.ainvoke(initial_state)

    logger.info("=" * 50)
    logger.info(f"Agent 完成")
    logger.info(f"寫入筆數：{final_state['written_count']}")
    logger.info(f"錯誤數量：{len(final_state['errors'])}")

    if final_state["errors"]:
        logger.warning("錯誤列表：")
        for err in final_state["errors"]:
            logger.warning(f"  - {err}")

    return final_state


if __name__ == "__main__":
    asyncio.run(main())