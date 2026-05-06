import os
import time
import schedule
import requests
from datetime import datetime
from supabase import create_client

# ─── CONFIG ───────────────────────────────────────────────────────────────────
SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_KEY", "")
RAPIDAPI_KEY = os.environ.get("RAPIDAPI_KEY", "")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# ─── RECHERCHES À SCRAPER ─────────────────────────────────────────────────────
SEARCHES = [
    {"query": "iPhone 15 Pro", "cat": "hightech", "emoji": "📱"},
    {"query": "AirPods Pro", "cat": "hightech", "emoji": "🎧"},
    {"query": "Samsung Galaxy S24", "cat": "hightech", "emoji": "📱"},
    {"query": "MacBook Air M3", "cat": "hightech", "emoji": "💻"},
    {"query": "PS5 Slim", "cat": "hightech", "emoji": "🎮"},
    {"query": "Dyson V15", "cat": "maison", "emoji": "🌪️"},
    {"query": "Nike Air Max", "cat": "mode", "emoji": "👟"},
    {"query": "Adidas Stan Smith", "cat": "mode", "emoji": "👟"},
    {"query": "aspirateur robot", "cat": "maison", "emoji": "🤖"},
    {"query": "cafetiere nespresso", "cat": "maison", "emoji": "☕"},
    {"query": "veste north face", "cat": "mode", "emoji": "🧥", "is_clothing": True},
    {"query": "jean levis 501", "cat": "mode", "emoji": "👖", "is_clothing": True},
    {"query": "trottinette electrique", "cat": "sport", "emoji": "🛴"},
    {"query": "television samsung 4k", "cat": "hightech", "emoji": "📺"},
    {"query": "lego technic", "cat": "jeux", "emoji": "🧱"},
]

FOOD_SEARCHES = [
    {"query": "boeuf", "store": "carrefour", "emoji": "🥩"},
    {"query": "saumon", "store": "leclerc", "emoji": "🐟"},
    {"query": "cafe", "store": "auchan", "emoji": "☕"},
    {"query": "vin rouge", "store": "lidl", "emoji": "🍷"},
    {"query": "pizza", "store": "leclerc", "emoji": "🍕"},
    {"query": "fromage", "store": "carrefour", "emoji": "🧀"},
]

def search_amazon(query, emoji, cat, is_clothing=False):
    """Recherche sur Amazon via RapidAPI"""
    try:
        url = "https://real-time-amazon-data.p.rapidapi.com/search"
        headers = {
            "X-RapidAPI-Key": RAPIDAPI_KEY,
            "X-RapidAPI-Host": "real-time-amazon-data.p.rapidapi.com"
        }
        params = {
            "query": query,
            "page": "1",
            "country": "FR",
            "sort_by": "RELEVANCE",
            "product_condition": "ALL"
        }
        resp = requests.get(url, headers=headers, params=params, timeout=10)
        if resp.status_code != 200:
            print(f"Amazon API error {resp.status_code} for {query}")
            return []

        data = resp.json()
        products = data.get("data", {}).get("products", [])
        results = []

        for p in products[:3]:
            price_str = p.get("product_price", "")
            orig_str = p.get("product_original_price", "") or price_str

            # Nettoie les prix
            price = parse_price(price_str)
            orig = parse_price(orig_str)
            if price <= 0:
                continue

            # Calcule la remise
            if orig > price:
                drop = round((orig - price) / orig * 100)
            else:
                drop = 0

            # Seulement si remise > 5%
            if drop < 5:
                continue

            product_id = f"amazon_{p.get('asin', '')}"
            image_url = p.get("product_photo", "")

            results.append({
                "id": product_id,
                "name": p.get("product_title", query)[:200],
                "category": cat,
                "emoji": emoji,
                "image_url": image_url,
                "current_price": price,
                "original_price": orig,
                "drop_percent": drop,
                "marketplace": "Amazon",
                "url": p.get("product_url", ""),
                "is_clothing": is_clothing,
                "updated_at": datetime.utcnow().isoformat(),
            })

        return results

    except Exception as e:
        print(f"Erreur Amazon search '{query}': {e}")
        return []


def search_fnac(query, emoji, cat, is_clothing=False):
    """Recherche sur Fnac via RapidAPI"""
    try:
        url = "https://fnac-search.p.rapidapi.com/search"
        headers = {
            "X-RapidAPI-Key": RAPIDAPI_KEY,
            "X-RapidAPI-Host": "fnac-search.p.rapidapi.com"
        }
        params = {"query": query, "lang": "fr"}
        resp = requests.get(url, headers=headers, params=params, timeout=10)
        if resp.status_code != 200:
            return []

        data = resp.json()
        results = []

        for p in data.get("results", [])[:2]:
            price = p.get("price", 0)
            orig = p.get("originalPrice", price)
            if price <= 0:
                continue
            drop = round((orig - price) / orig * 100) if orig > price else 0
            if drop < 5:
                continue

            results.append({
                "id": f"fnac_{p.get('id', '')}",
                "name": p.get("name", query)[:200],
                "category": cat,
                "emoji": emoji,
                "image_url": p.get("imageUrl", ""),
                "current_price": price,
                "original_price": orig,
                "drop_percent": drop,
                "marketplace": "Fnac",
                "url": p.get("url", ""),
                "is_clothing": is_clothing,
                "updated_at": datetime.utcnow().isoformat(),
            })
        return results
    except Exception as e:
        print(f"Erreur Fnac search '{query}': {e}")
        return []


def parse_price(price_str):
    """Convertit '1 299,99 €' ou '$1,299.99' en float"""
    if not price_str:
        return 0.0
    try:
        cleaned = price_str.replace("€", "").replace("$", "").replace("£", "")
        cleaned = cleaned.replace(" ", "").replace("\xa0", "")
        # Format européen : 1.299,99 -> 1299.99
        if "," in cleaned and "." in cleaned:
            cleaned = cleaned.replace(".", "").replace(",", ".")
        elif "," in cleaned:
            cleaned = cleaned.replace(",", ".")
        return float(cleaned.strip())
    except:
        return 0.0


def save_products(products):
    """Sauvegarde les produits dans Supabase"""
    if not products:
        return
    try:
        for p in products:
            # Upsert (insert ou update si déjà existant)
            supabase.table("products").upsert(p).execute()

            # Historique des prix
            supabase.table("price_history").insert({
                "product_id": p["id"],
                "price": p["current_price"],
                "marketplace": p["marketplace"],
                "recorded_at": datetime.utcnow().isoformat(),
            }).execute()

        print(f"✅ {len(products)} produits sauvegardés")
    except Exception as e:
        print(f"Erreur Supabase save: {e}")


def run_scraping():
    """Lance le scraping complet"""
    print(f"\n🔍 Démarrage scraping — {datetime.now().strftime('%H:%M:%S')}")
    total = 0

    for search in SEARCHES:
        # Amazon
        products = search_amazon(
            search["query"],
            search["emoji"],
            search["cat"],
            search.get("is_clothing", False)
        )
        if products:
            save_products(products)
            total += len(products)

        # Pause pour éviter de surcharger l'API
        time.sleep(2)

        # Fnac pour les produits high-tech
        if search["cat"] == "hightech":
            products_fnac = search_fnac(
                search["query"],
                search["emoji"],
                search["cat"]
            )
            if products_fnac:
                save_products(products_fnac)
                total += len(products_fnac)
            time.sleep(1)

    print(f"✅ Scraping terminé — {total} produits mis à jour")


def run_food_scraping():
    """Scrape les promos alimentaires"""
    print(f"\n🥗 Scraping alimentaire — {datetime.now().strftime('%H:%M:%S')}")
    # Pour l'alimentaire on utilise des données simulées enrichies
    # (les APIs alimentaires FR sont très limitées en gratuit)
    food_items = [
        {"id":"f_boeuf","name":"Filet de bœuf","unit":"500g","emoji":"🥩","store":"carrefour","current_price":7.99,"original_price":12.50,"drop_percent":36,"image_url":"https://images.unsplash.com/photo-1546964124-0cce460f38ef?w=300"},
        {"id":"f_saumon","name":"Saumon fumé Label Rouge","unit":"200g","emoji":"🐟","store":"leclerc","current_price":5.90,"original_price":9.95,"drop_percent":41,"image_url":"https://images.unsplash.com/photo-1519708227418-c8fd9a32b7a2?w=300"},
        {"id":"f_cafe","name":"Café Lavazza 1kg","unit":"1kg","emoji":"☕","store":"auchan","current_price":9.99,"original_price":15.40,"drop_percent":35,"image_url":"https://images.unsplash.com/photo-1447933601403-0c6688de566e?w=300"},
        {"id":"f_vin","name":"Bordeaux Rouge Millésime","unit":"75cl","emoji":"🍷","store":"lidl","current_price":6.49,"original_price":11.99,"drop_percent":46,"image_url":"https://images.unsplash.com/photo-1510812431401-41d2bd2722f3?w=300"},
        {"id":"f_pizza","name":"Pizza Margherita x2","unit":"x2","emoji":"🍕","store":"leclerc","current_price":3.49,"original_price":5.99,"drop_percent":42,"image_url":"https://images.unsplash.com/photo-1565299624946-b28f40a0ae38?w=300"},
        {"id":"f_fromage","name":"Plateau fromages 400g","unit":"400g","emoji":"🧀","store":"intermarche","current_price":4.20,"original_price":6.80,"drop_percent":38,"image_url":""},
        {"id":"f_granola","name":"Granola Bio 750g","unit":"750g","emoji":"🥣","store":"aldi","current_price":2.79,"original_price":4.99,"drop_percent":44,"image_url":""},
        {"id":"f_poulet","name":"Poulet rôti Label Rouge","unit":"1 pièce","emoji":"🍗","store":"carrefour","current_price":8.99,"original_price":13.50,"drop_percent":33,"image_url":""},
        {"id":"f_jus","name":"Jus d'orange Innocent 1L","unit":"1L","emoji":"🍊","store":"monoprix","current_price":2.49,"original_price":3.99,"drop_percent":38,"image_url":""},
        {"id":"f_pates","name":"Pâtes Barilla 5kg","unit":"5kg","emoji":"🍝","store":"leclerc","current_price":6.99,"original_price":11.50,"drop_percent":39,"image_url":""},
    ]

    try:
        for item in food_items:
            item["updated_at"] = datetime.utcnow().isoformat()
            supabase.table("food_products").upsert(item).execute()
        print(f"✅ {len(food_items)} produits alimentaires mis à jour")
    except Exception as e:
        print(f"Erreur food save: {e}")


def main():
    print("🚀 DropHunt Scraper démarré")
    print(f"Supabase: {SUPABASE_URL[:40]}...")
    print(f"RapidAPI: {'✅ configuré' if RAPIDAPI_KEY else '❌ manquant'}")

    # Lance immédiatement au démarrage
    run_scraping()
    run_food_scraping()

    # Puis 3x par jour : 8h, 13h, 19h
    schedule.every().day.at("08:00").do(run_scraping)
    schedule.every().day.at("13:00").do(run_scraping)
    schedule.every().day.at("19:00").do(run_scraping)
    schedule.every().day.at("08:30").do(run_food_scraping)
    schedule.every().day.at("13:30").do(run_food_scraping)
    schedule.every().day.at("19:30").do(run_food_scraping)

    print("⏰ Scheduler actif — scraping 3x/jour")

    while True:
        schedule.run_pending()
        time.sleep(60)


if __name__ == "__main__":
    main()