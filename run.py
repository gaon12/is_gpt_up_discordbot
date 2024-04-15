import discord
from discord.ext import commands
import requests
import datetime
import pytz
from dotenv import load_dotenv
import os
from googletrans import Translator
import feedparser
import html
import re  # 정규 표현식 사용을 위해 추가

load_dotenv()  # 환경 변수 파일 로딩
TOKEN = os.getenv('DISCORD_TOKEN')  # .env 파일에서 디스코드 토큰 읽기

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True  # 메시지 내용 접근을 위한 인텐트 활성화
bot = commands.Bot(command_prefix='!', intents=intents)
translator = Translator()  # 번역기 객체 생성

def fetch_data(url):
    # URL에서 데이터를 가져와 JSON 형식으로 반환
    response = requests.get(url)
    return response.json()

def get_timezone(data):
    # 데이터에서 시간대 정보 추출
    return pytz.timezone(data["page"]["time_zone"])

def check_components_issues(data, days_back, tz):
    # 지정된 일수 내의 컴포넌트 이슈 검사
    today = datetime.datetime.now(tz)
    components = {comp["name"]: [] for comp in data["components"]}
    incidents = data["incidents"]

    for incident in incidents:
        incident_date = datetime.datetime.fromisoformat(incident["created_at"]).astimezone(tz)
        
        if (today - incident_date).days <= days_back:
            for update in incident.get("incident_updates", []):
                affected_components = update.get("affected_components", [])
                for component in affected_components:
                    if component["old_status"] != "operational":
                        comp_name = component["name"]
                        components[comp_name].append(
                            (incident_date.date(), update["body"])
                        )

    return components

def clean_html(raw_html):
    """HTML 태그와 엔티티를 정리하는 함수"""
    clean_text = html.unescape(raw_html)  # HTML 엔티티를 일반 텍스트로 변환
    clean_text = re.sub('<.*?>', '', clean_text)  # HTML 태그 제거
    return clean_text

def split_messages(message, limit=2000):
    # 메시지를 분할하는 함수
    return [message[i:i+limit] for i in range(0, len(message), limit)]

@bot.command()
async def isgptup(ctx, service=None, days: int = 1):
    message = await ctx.send("Loading...")
    try:
        # service가 None이거나 all일 때 동일하게 처리하도록 변경
        if service is None or service == 'all' or service.isdigit() or service in ['API', 'ChatGPT', 'Labs', 'Playground', 'helpme', 'issue']:
            if service and service.isdigit():
                days = int(service)
                service = 'all'  # 숫자만 들어오면 all로 처리
            if days < 1 or days > 90:
                await message.edit(content="Please enter a valid number of days between 1 and 90.")
                return

            url = "https://status.openai.com/index.json"
            status_url = "https://status.openai.com/api/v2/status.json"
            
            status_data = fetch_data(status_url)
            tz = get_timezone(status_data)
            data = fetch_data(url)
            problems = check_components_issues(data, days, tz)

            response_text = ""
            full_translation = ""
            if service in ['API', 'ChatGPT', 'Labs', 'Playground']:
                issues = problems.get(service, [])
                response_text += f"> **{service} Status in the last {days} days:**\n"
                if issues:
                    for date, issue in issues:
                        response_text += f"  > `Date: {date}, Issue: {issue}`\n"
                        full_translation += f"Date: {date}, Issue: {issue}\n"
                else:
                    response_text += "  > No issues reported.\n"
            else:  # all을 처리하는 로직을 기본으로 사용
                response_text += f"**All Services Status in the last {days} days:**\n"
                for service_name, issues in problems.items():
                    response_text += f"\n> **Service: {service_name}**\n"
                    if issues:
                        for date, issue in issues:
                            response_text += f"  > `Date: {date}, Issue: {issue}`\n"
                            full_translation += f"Date: {date}, Issue: {issue}\n"
                    else:
                        response_text += "  > No issues reported.\n"
            # 메시지를 분할하여 전송
            for part in split_messages(response_text):
                await ctx.send(part)
            if full_translation:
                translation = translator.translate(full_translation, src='en', dest='ko')
                # 번역된 결과를 Markdown 포맷으로 출력합니다.
                translation_text = f"**Translated Issues:**\n```{translation.text}```"
                for part in split_messages(translation_text):
                    await ctx.send(part)
        else:
            await message.edit(content="**Invalid service name. Please use 'API', 'ChatGPT', 'Labs', 'Playground', or 'all'.**")
    except discord.HTTPException as e:
        if e.code == 50035:
            # Handling message too long error specifically
            await message.edit(content=f"**Too many issue items, try again with a date range smaller than current ({days})!**")
        else:
            raise e

bot.run(TOKEN)
