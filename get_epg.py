import re
import json
import requests
from datetime import datetime, timedelta
import xml.etree.ElementTree as ET
from xml.dom import minidom

URL_SITE = "https://latinasat.com.br/"
CHANNEL_ID = "latinasat.br"
CHANNEL_NAME = "Latina Sat Brasil"

def get_start_of_week():
    """Retorna o domingo da semana atual como ponto de partida (Dia 0)"""
    today = datetime.now()
    idx = (today.weekday() + 1) % 7  # Ajusta Seg=0 para Dom=0
    return today - timedelta(days=idx)

def format_xmltv_date(base_date, time_str):
    """Combina a data base com 'HH:MM' no padrão XMLTV (-0300)"""
    try:
        hours, minutes = map(int, time_str.split(':'))
        dt = base_date.replace(hour=hours, minute=minutes, second=0, microsecond=0)
        return dt.strftime("%Y%m%d%H%M%S -0300")
    except Exception:
        return None

def fetch_schedule_from_site():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    print("Acessando o site para buscar o código fonte original...")
    try:
        response = requests.get(URL_SITE, headers=headers, timeout=15)
        if response.status_code != 200:
            return None
        
        html_content = response.text

        # 1. Procura a variável nas tags <script> do HTML principal ou nos arquivos JS
        scripts = re.findall(r'<script.*?>(.*?)</script>', html_content, re.DOTALL)
        
        js_files = re.findall(r'src=["\'](.*?\.(?:js|ts))["\']', html_content)
        for src in js_files:
            js_url = src if src.startswith('http') else f"{URL_SITE.rstrip('/')}/{src.lstrip('/')}"
            try:
                js_res = requests.get(js_url, headers=headers, timeout=5)
                if js_res.status_code == 200:
                    scripts.append(js_res.text)
            except Exception:
                continue

        for content in scripts:
            if "WEEKLY_SCHEDULE" in content:
                # Captura o bloco do objeto WEEKLY_SCHEDULE
                match = re.search(r'const\s+WEEKLY_SCHEDULE\s*=\s*(\{.*?\});', content, re.DOTALL)
                if match:
                    js_text = match.group(1)
                    
                    # Limpeza agressiva e segura para gerar um JSON válido:
                    # Remove comentários de linha (// ...)
                    js_text = re.sub(r'//.*', '', js_text)
                    # Força aspas duplas em todas as chaves (ex: start: -> "start":)
                    js_text = re.sub(r'([{,\s])(\w+)\s*:', r'\1"\2":', js_text)
                    # Transforma aspas simples em aspas duplas nos valores
                    js_text = re.sub(r"'\s*(.*?)\s*'", r'"\1"', js_text)
                    # Remove espaços em branco extras e quebras de linha que quebram o parser
                    js_text = re.sub(r'\s+', ' ', js_text)
                    # Remove vírgulas trapaceiras no final de arrays/objetos: ex: [1, 2, ] -> [1, 2]
                    js_text = re.sub(r',\s*([\]}])', r'\1', js_text)
                    
                    # Garante que as chaves dos dias fiquem estritamente entre aspas duplas
                    js_text = re.sub(r'([{,])\s*([0-6]|default|Monday|Wednesday|Thursday|Saturday)\s*:', r'\1"\2":', js_text)

                    return json.loads(js_text)
                    
    except Exception as e:
        print(f"Erro durante a varredura automática: {e}")
        
    return None

def generate_automated_xml():
    weekly_data = fetch_schedule_from_site()
    
    if not weekly_data:
        print("Não foi possível extrair a programação diretamente do site por varredura automática.")
        return

    print("Programação encontrada e decodificada com sucesso! Construindo a grade EPG...")

    # Mapeamento para normalizar os nomes dos dias usados no código do site
    day_mapping = {
        "Sunday": 0, "0": 0,
        "default": 1, "Monday": 1, "1": 1,
        "2": 2, "Tuesday": 2,
        "3": 3, "Wednesday": 3,
        "4": 4, "Thursday": 4,
        "5": 5, "Friday": 5,
        "6": 6, "Saturday": 6
    }

    tv = ET.Element("tv", generator_info_name="LatinaSat EPG Extractor")
    channel = ET.SubElement(tv, "channel", id=CHANNEL_ID)
    ET.SubElement(channel, "display-name").text = CHANNEL_NAME

    start_of_week = get_start_of_week()

    for day_key, programs in weekly_data.items():
        day_offset = day_mapping.get(day_key)
        if day_offset is None:
            try:
                day_offset = int(day_key)
            except:
                continue
                
        program_date = start_of_week + timedelta(days=day_offset)
        
        for p in programs:
            title = p.get("label") or p.get("title") or "Programação LatinaSat"
            desc = p.get("desc", "")
            
            start_time = p.get("start")
            end_time = p.get("end")
            
            if not start_time or not end_time:
                continue

            start_xml = format_xmltv_date(program_date, start_time)
            end_xml = format_xmltv_date(program_date, end_time)

            if end_time == "00:00":
                end_program_date = program_date + timedelta(days=1)
                end_xml = format_xmltv_date(end_program_date, "00:00")
            elif end_time < start_time:
                end_program_date = program_date + timedelta(days=1)
                end_xml = format_xmltv_date(end_program_date, end_time)

            if start_xml and end_xml:
                programme = ET.SubElement(tv, "programme", {
                    "start": start_xml,
                    "stop": end_xml,
                    "channel": CHANNEL_ID
                })
                ET.SubElement(programme, "title", lang="pt").text = title
                if desc:
                    ET.SubElement(programme, "desc", lang="pt").text = desc

    xml_str = minidom.parseString(ET.tostring(tv, 'utf-8')).toprettyxml(indent="  ")
    with open("latinasat_epg.xml", "w", encoding="utf-8") as f:
        f.write(xml_str)
        
    print("[SUCESSO] O arquivo 'latinasat_epg.xml' foi gerado e atualizado direto da web!")

if __name__ == "__main__":
    generate_automated_xml()
