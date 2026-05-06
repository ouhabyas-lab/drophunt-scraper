import os
import time
import schedule
import requests
from datetime import datetime
from supabase import create_client

SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_KEY", "")
RAPIDAPI_KEY = os.environ.get("RAPIDAPI_KEY", "")

print(f"SUPABASE_URL: {SUPABASE_URL[:30] if SUPABASE_URL else 'MANQUANT'}")
print(f"SUPABASE_KEY: {'OK' if SUPABASE_KEY else 'MANQUANT'}")
print(f"RAPIDAPI_KEY: {'OK' if RAPIDAPI_KEY else 'MANQUANT'}")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("Variables manquantes - chargement des données de démo")
    supabase = None
else:
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

DEMO_PRODUCTS = [
    {"id":"a1","name":"iPhone 15 Pro 256GB","category":"hightech","emoji":"📱","image_url":"https://images.unsplash.com/photo-1695048133142-1a20484429be?w=300","current_price":799,"original_price":979,"drop_percent":18,"marketplace":"Amazon","is_clothing":False},
    {"id":"a2","name":"AirPods Pro 2e gen","category":"hightech","emoji":"🎧","image_url":"https://images.unsplash.com/photo-1600294037681-c80b4cb5b434?w=300","current_price":189,"original_price":279,"drop_percent":32,"marketplace":"Fnac","is_clothing":False},
    {"id":"a3","name":"Samsung Galaxy S24","category":"hightech","emoji":"📱","image_url":"https://images.unsplash.com/photo-1610945265064-0e34e5519bbf?w=300","current_price":699,"original_price":899,"drop_percent":22,"marketplace":"Cdiscount","is_clothing":False},
    {"id":"a4","name":"Dyson V15 Detect","category":"maison","emoji":"🌪️","image_url":"https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=300","current_price":379,"original_price":599,"drop_percent":37,"marketplace":"Cdiscount","is_clothing":False},
    {"id":"a5","name":"PS5 Slim + Manette","category":"hightech","emoji":"🎮","image_url":"https://images.unsplash.com/photo-1606813907291-d86efa9b94db?w=300","current_price":399,"original_price":499,"drop_percent":20,"marketplace":"Fnac","is_clothing":False},
    {"id":"a6","name":"MacBook Air M3","category":"hightech","emoji":"💻","image_url":"https://images.unsplash.com/photo-1517336714731-489689fd1ca8?w=300","current_price":1099,"original_price":1499,"drop_percent":27,"marketplace":"Fnac","is_clothing":False},
    {"id":"a7","name":"Nike Air Max 90","category":"mode","emoji":"👟","image_url":"https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=300","current_price":89,"original_price":139,"drop_percent":36,"marketplace":"Zalando","is_clothing":True},
    {"id":"a8","name":"Veste The North Face","category":"mode","emoji":"🧥","image_url":"https://images.unsplash.com/photo-1539533018447-63fcce2678e3?w=300","current_price":119,"original_price":220,"drop_percent":46,"marketplace":"Zalando","is_clothing":True},
    {"id":"a9","name":"Jean Levi's 501","category":"mode","emoji":"👖","image_url":"https://images.unsplash.com/photo-1542272604-787c3835535d?w=300","current_price":59,"original_price":120,"drop_percent":51,"marketplace":"Zalando","is_clothing":True},
    {"id":"a10","name":"Aspirateur Rowenta","category":"maison","emoji":"🫧","image_url":"https://images.unsplash.com/photo-1558317374-067fb5f30001?w=300","current_price":89,"original_price":179,"drop_percent":50,"marketplace":"Amazon","is_clothing":False},
    {"id":"a11","name":"Cafetière Nespresso","category":"maison","emoji":"☕","image_url":"https://images.unsplash.com/photo-1495474472287-4d71bcdd2085?w=300","current_price":79,"original_price":149,"drop_percent":47,"marketplace":"Amazon","is_clothing":False},
    {"id":"a12","name":"Trottinette électrique","category":"sport","emoji":"🛴","image_url":"https://images.unsplash.com/photo-1558618047-3c8c76ca7d13?w=300","current_price":299,"original_price":499,"drop_percent":40,"marketplace":"Cdiscount","is_clothing":False},
]

DEMO_FOOD = [
    {"id":"f1","name":"Filet de bœuf","category":"Viandes","emoji":"🥩","image_url":"https://images.unsplash.com/photo-1546964124-0cce460f38ef?w=300","store":"carrefour","current_price":7.99,"original_price":12.50,"drop_percent":36,"unit":"500g"},
    {"id":"f2","name":"Café Lavazza 1kg","category":"Épicerie","emoji":"☕","image_url":"https://images.unsplash.com/photo-1447933601403-0c6688de566e?w=300","store":"auchan","current_price":9.99,"original_price":15.40,"drop_percent":35,"unit":"1kg"},
    {"id":"f3","name":"Bordeaux Rouge","category":"Vins","emoji":"🍷","image_url":"https://images.unsplash.com/photo-1510812431401-41d2bd2722f3?w=300","store":"lidl","current_price":6.49,"original_price":11.99,"drop_percent":46,"unit":"75cl"},
    {"id":"f4","name":"Saumon fumé LR","category":"Poissons","emoji":"🐟","image_url":"https://images.unsplash.com/photo-1519708227418-c8fd9a32b7a2?w=300","store":"leclerc","current_price":5.90,"original_price":9.95,"drop_percent":41,"unit":"200g"},
    {"id":"f5","name":"Pizza Margherita x2","category":"Surgelés","emoji":"🍕","image_url":"https://images.unsplash.com/photo-1565299624946-b28f40a0ae38?w=300","store":"leclerc","current_price":3.49,"original_price":5.99,"drop_percent":42,"unit":"x2"},
    {"id":"f6","name":"Granola Bio 750g","category":"Bio","emoji":"🥣","image_url":"","store":"aldi","current_price":2.79,"original_price":4.99,"drop_percent":44,"unit":"750g"},
    {"id":"f7","name":"Plateau fromages","category":"Crémerie","emoji":"🧀","image_url":"","store":"intermarche","current_price":4.20,"original_price":6.80,"drop_percent":38,"unit":"400g"},
    {"id":"f8","name":"Poulet rôti LR","category":"Viandes","emoji":"🍗","image_url":"","store":"carrefour","current_price":8.99,"original_price":13.50,"drop_percent":33,"unit":"1 pièce"},
]

def try_amazon_search(query, cat, emoji, is_clothing=False):
    if not RAPIDAPI_KEY:
        return []
    try:
        url = "https://real-time-amazon-data.p.rapidapi.com/search"
        headers = {"X-RapidAPI-Key": RAPIDAPI_KEY, "X-RapidAPI-Host": "real-time-amazon-data.p.rapidapi.com"}
        params = {"query": query, "page": "1", "country": "FR"}
        resp = requests.get(url, headers=headers, params=params, timeout=15)
        if resp.status_code != 200:
            return []
        products = resp.json().get("data", {}).get("products", [])
        results = []
        for p in products[:2]:
            price = parse_price(p.get("product_price", ""))
            orig = parse_price(p.get("product_original_price", "")) or price * 1.2
            if price <= 0 or orig <= price:
                continue
            drop = round((orig - price) / orig * 100)
            if drop < 10:
                continue
            results.append({
                "id": f"amz_{p.get('asin','')}",
                "name": p.get("product_title", query)[:200],
                "category": cat, "emoji": emoji,
                "image_url": p.get("product_photo", ""),
                "current_price": price, "original_price": orig,
                "drop_percent": drop, "marketplace": "Amazon",
                "url": p.get("product_url", ""),
                "is_clothing": is_clothing,
                "updated_at": datetime.utcnow().isoformat(),
            })
        return results
    except Exception as e:
        print(f"Amazon error '{query}': {e}")
        return []

def parse_price(s):
    if not s:
        return 0.0
    try:
        c = s.replace("€","").replace("$","").replace(" ","").replace("\xa0","")
        if "," in c and "." in c:
            c = c.replace(".","").replace(",",".")
        elif "," in c:
            c = c.replace(",",".")
        return float(c.strip())
    except:
        return 0.0

def save_to_supabase(table, items):
    if not supabase or not items:
        return
    try:
        for item in items:
            item["updated_at"] = datetime.utcnow().isoformat()
            supabase.table(table).upsert(item).execute()
        print(f"✅ {len(items)} items -> {table}")
    except Exception as e:
        print(f"Supabase error: {e}")

def run_all():
    print(f"\n🔍 Scraping {datetime.now().strftime('%H:%M:%S')}")
    
    # 1. Charge les données de démo en base (toujours)
    save_to_supabase("products", DEMO_PRODUCTS)
    save_to_supabase("food_products", DEMO_FOOD)
    
    # 2. Essaie d'enrichir avec Amazon si la clé est dispo
    if RAPIDAPI_KEY:
        searches = [
            ("iPhone 15 Pro", "hightech", "📱"),
            ("Dyson aspirateur", "maison", "🌪️"),
            ("Nike sneakers", "mode", "👟", True),
        ]
        for args in searches:
            results = try_amazon_search(*args)
            if results:
                save_to_supabase("products", results)
            time.sleep(3)
    
    print("✅ Done")

print("🚀 DropHunt Scraper starting...")
run_all()

schedule.every().day.at("08:00").do(run_all)
schedule.every().day.at("13:00").do(run_all)
schedule.every().day.at("19:00").do(run_all)

print("⏰ Scheduler actif")
while True:
    schedule.run_pending()
    time.sleep(60)
