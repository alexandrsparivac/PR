#!/usr/bin/env python3
"""
Aplicație HTTP client pentru magazin online
- Operațiuni CRUD pentru categorii și produse
- Comunicare cu API HTTP
"""

import requests
import json
import os
from datetime import datetime

# Configurare
BASE_URL = "http://localhost:8000/api"  # Poți modifica URL-ul serverului
HEADERS = {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
}

# Culori pentru terminal
COLORS = {
    'red': '\033[91m',
    'green': '\033[92m',
    'yellow': '\033[93m',
    'blue': '\033[94m',
    'magenta': '\033[95m',
    'cyan': '\033[96m',
    'white': '\033[97m',
    'bold': '\033[1m',
    'reset': '\033[0m',
    'header': '\033[95m\033[1m',
    'success': '\033[92m\033[1m',
    'error': '\033[91m\033[1m',
    'info': '\033[94m\033[1m',
    'warning': '\033[93m\033[1m',
    'result': '\033[96m',
    'command': '\033[93m'
}

def color_print(text, color='white'):
    """Afișează text cu culoare."""
    if os.name == 'nt':  # Windows - fără culori
        print(text)
    else:
        print(f"{COLORS.get(color, COLORS['white'])}{text}{COLORS['reset']}")

def color_input(prompt, color='command'):
    """Input cu culoare."""
    if os.name == 'nt':  # Windows - fără culori
        return input(prompt)
    else:
        return input(f"{COLORS.get(color, COLORS['white'])}{prompt}{COLORS['reset']}")

def print_header(text):
    """Afișează un header decorat."""
    separator = "=" * 60
    color_print(separator, 'header')
    color_print(f"{text:^60}", 'header')
    color_print(separator, 'header')

def print_section(title):
    """Afișează o secțiune."""
    color_print(f"\n{'─' * 50}", 'info')
    color_print(f"  {title}", 'info')
    color_print(f"{'─' * 50}", 'info')

def print_result(label, value):
    """Afișează un rezultat formatat."""
    color_print(f"  {label}: ", 'info')
    color_print(value, 'result')

def print_list_item(index, item):
    """Afișează un element din listă."""
    color_print(f"  [{index}] ", 'yellow')
    color_print(item, 'result')

def show_main_menu():
    """Afișează meniul principal."""
    print_header("🛒 MAGAZIN ONLINE - CLIENT HTTP")
    
    color_print("📝 Meniu principal:", 'info')
    color_print("  1. Gestionare Categorii", 'info')
    color_print("  2. Gestionare Produse", 'info')
    color_print("  3. Configurare Server", 'info')
    color_print("  4. Ieșire", 'info')
    color_print("──────────────────────────────────────────────────", 'info')

def show_category_menu():
    """Afișează meniul pentru categorii."""
    print_section("📂 GESTIONARE CATEGORII")
    
    color_print("  1. Listează toate categoriile", 'info')
    color_print("  2. Vezi detalii categorie", 'info')
    color_print("  3. Creează categorie nouă", 'info')
    color_print("  4. Modifică categorie", 'info')
    color_print("  5. Șterge categorie", 'info')
    color_print("  6. Înapoi la meniul principal", 'info')
    color_print("──────────────────────────────────────────────────", 'info')

def show_product_menu():
    """Afișează meniul pentru produse."""
    print_section("📦 GESTIONARE PRODUSE")
    
    color_print("  1. Listează produsele dintr-o categorie", 'info')
    color_print("  2. Creează produs nou", 'info')
    color_print("  3. Înapoi la meniul principal", 'info')
    color_print("──────────────────────────────────────────────────", 'info')

def make_request(method, endpoint, data=None):
    """Face o cerere HTTP către API."""
    url = f"{BASE_URL}{endpoint}"
    
    try:
        if method.upper() == 'GET':
            response = requests.get(url, headers=HEADERS)
        elif method.upper() == 'POST':
            response = requests.post(url, headers=HEADERS, json=data)
        elif method.upper() == 'PUT':
            response = requests.put(url, headers=HEADERS, json=data)
        elif method.upper() == 'DELETE':
            response = requests.delete(url, headers=HEADERS)
        else:
            color_print(f"✗ EROARE: Metodă HTTP invalidă: {method}", 'error')
            return None
        
        return response
    
    except requests.exceptions.ConnectionError:
        color_print("✗ EROARE: Nu se poate conecta la server. Verifică URL-ul și dacă serverul rulează.", 'error')
        return None
    except requests.exceptions.Timeout:
        color_print("✗ EROARE: Timeout la conectarea cu serverul.", 'error')
        return None
    except requests.exceptions.RequestException as e:
        color_print(f"✗ EROARE: Cerere eșuată: {e}", 'error')
        return None

def list_categories():
    """Listează toate categoriile."""
    print_section("📂 LISTĂ CATEGORII")
    
    response = make_request('GET', '/categories')
    
    if response and response.status_code == 200:
        categories = response.json()
        
        if not categories:
            color_print("ℹ  Nu există categorii în magazin.", 'warning')
            return []
        
        color_print(f"✓ S-au găsit {len(categories)} categorii:", 'success')
        for i, category in enumerate(categories, 1):
            print_list_item(i, f"ID: {category.get('id', 'N/A')} - {category.get('title', 'N/A')}")
            color_print(f"      Descriere: {category.get('description', 'N/A')}", 'result')
        
        return categories
    
    elif response:
        color_print(f"✗ EROARE: {response.status_code} - {response.text}", 'error')
    
    return []

def get_category_details():
    """Afișează detalii despre o categorie specifică."""
    category_id = color_input("Introdu ID-ul categoriei: ")
    
    if not category_id:
        color_print("✗ EROARE: ID-ul categoriei nu poate fi gol.", 'error')
        return
    
    print_section(f"📂 DETALII CATEGORIE #{category_id}")
    
    response = make_request('GET', f'/categories/{category_id}')
    
    if response and response.status_code == 200:
        category = response.json()
        
        color_print("✓ Detalii categorie:", 'success')
        print_result("ID", category.get('id', 'N/A'))
        print_result("Titlu", category.get('title', 'N/A'))
        print_result("Descriere", category.get('description', 'N/A'))
        print_result("Creat la", category.get('created_at', 'N/A'))
        print_result("Actualizat la", category.get('updated_at', 'N/A'))
        
        # Afișează și produsele dacă există
        products = category.get('products', [])
        if products:
            color_print(f"\n📦 Produse în această categorie ({len(products)}):", 'info')
            for i, product in enumerate(products, 1):
                print_list_item(i, f"ID: {product.get('id', 'N/A')} - {product.get('name', 'N/A')}")
                color_print(f"      Preț: {product.get('price', 'N/A')} MDL", 'result')
        else:
            color_print("\nℹ  Nu există produse în această categorie.", 'warning')
    
    elif response and response.status_code == 404:
        color_print(f"✗ EROARE: Categoria cu ID {category_id} nu există.", 'error')
    elif response:
        color_print(f"✗ EROARE: {response.status_code} - {response.text}", 'error')

def create_category():
    """Creează o categorie nouă."""
    print_section("📂 CREARE CATEGORIE NOUĂ")
    
    title = color_input("Titlu categorie: ")
    if not title:
        color_print("✗ EROARE: Titlul nu poate fi gol.", 'error')
        return
    
    description = color_input("Descriere categorie (opțional): ")
    
    category_data = {
        'title': title,
        'description': description
    }
    
    response = make_request('POST', '/categories', category_data)
    
    if response and response.status_code == 201:
        category = response.json()
        color_print("✓ Categoria a fost creată cu succes!", 'success')
        print_result("ID", category.get('id', 'N/A'))
        print_result("Titlu", category.get('title', 'N/A'))
        print_result("Descriere", category.get('description', 'N/A'))
    
    elif response:
        color_print(f"✗ EROARE: {response.status_code} - {response.text}", 'error')

def update_category():
    """Modifică titlul unei categorii."""
    category_id = color_input("Introdu ID-ul categoriei de modificat: ")
    
    if not category_id:
        color_print("✗ EROARE: ID-ul categoriei nu poate fi gol.", 'error')
        return
    
    print_section(f"📂 MODIFICARE CATEGORIE #{category_id}")
    
    # Mai întâi afișăm detaliile curente
    response = make_request('GET', f'/categories/{category_id}')
    
    if response and response.status_code == 200:
        category = response.json()
        color_print("ℹ  Detalii curente:", 'info')
        print_result("Titlu curent", category.get('title', 'N/A'))
        print_result("Descriere curentă", category.get('description', 'N/A'))
        
        new_title = color_input(f"Titlu nou (lăsă gol pentru a păstra '{category.get('title', 'N/A')}'): ")
        new_description = color_input(f"Descriere nouă (lăsă gol pentru a păstra '{category.get('description', 'N/A')}'): ")
        
        update_data = {}
        if new_title:
            update_data['title'] = new_title
        if new_description:
            update_data['description'] = new_description
        
        if not update_data:
            color_print("ℹ  Nu s-au făcut modificări.", 'warning')
            return
        
        response = make_request('PUT', f'/categories/{category_id}', update_data)
        
        if response and response.status_code == 200:
            updated_category = response.json()
            color_print("✓ Categoria a fost actualizată cu succes!", 'success')
            print_result("Titlu nou", updated_category.get('title', 'N/A'))
            print_result("Descriere nouă", updated_category.get('description', 'N/A'))
        elif response:
            color_print(f"✗ EROARE: {response.status_code} - {response.text}", 'error')
    
    elif response and response.status_code == 404:
        color_print(f"✗ EROARE: Categoria cu ID {category_id} nu există.", 'error')
    elif response:
        color_print(f"✗ EROARE: {response.status_code} - {response.text}", 'error')

def delete_category():
    """Șterge o categorie."""
    category_id = color_input("Introdu ID-ul categoriei de șters: ")
    
    if not category_id:
        color_print("✗ EROARE: ID-ul categoriei nu poate fi gol.", 'error')
        return
    
    # Confirmare
    confirm = color_input(f"🚨 Ești sigur că vrei să ștergi categoria #{category_id}? (da/nu): ")
    
    if confirm.lower() != 'da':
        color_print("ℹ  Operațiune anulată.", 'warning')
        return
    
    print_section(f"🗑️ ȘTERGERE CATEGORIE #{category_id}")
    
    response = make_request('DELETE', f'/categories/{category_id}')
    
    if response and response.status_code == 200:
        color_print("✓ Categoria a fost ștearsă cu succes!", 'success')
    elif response and response.status_code == 404:
        color_print(f"✗ EROARE: Categoria cu ID {category_id} nu există.", 'error')
    elif response:
        color_print(f"✗ EROARE: {response.status_code} - {response.text}", 'error')

def list_products_in_category():
    """Listează produsele dintr-o categorie."""
    category_id = color_input("Introdu ID-ul categoriei: ")
    
    if not category_id:
        color_print("✗ EROARE: ID-ul categoriei nu poate fi gol.", 'error')
        return
    
    print_section(f"📦 PRODUSE ÎN CATEGORIA #{category_id}")
    
    response = make_request('GET', f'/categories/{category_id}/products')
    
    if response and response.status_code == 200:
        products = response.json()
        
        if not products:
            color_print("ℹ  Nu există produse în această categorie.", 'warning')
            return
        
        color_print(f"✓ S-au găsit {len(products)} produse:", 'success')
        for i, product in enumerate(products, 1):
            print_list_item(i, f"ID: {product.get('id', 'N/A')} - {product.get('name', 'N/A')}")
            print_result("  Preț", f"{product.get('price', 'N/A')} MDL")
            print_result("  Descriere", product.get('description', 'N/A'))
            print_result("  Stoc", product.get('stock', 'N/A'))
            color_print("", 'white')
    
    elif response and response.status_code == 404:
        color_print(f"✗ EROARE: Categoria cu ID {category_id} nu există.", 'error')
    elif response:
        color_print(f"✗ EROARE: {response.status_code} - {response.text}", 'error')

def create_product():
    """Creează un produs nou într-o categorie."""
    print_section("📦 CREARE PRODUS NOU")
    
    category_id = color_input("Introdu ID-ul categoriei: ")
    
    if not category_id:
        color_print("✗ EROARE: ID-ul categoriei nu poate fi gol.", 'error')
        return
    
    # Verificăm dacă există categoria
    response = make_request('GET', f'/categories/{category_id}')
    
    if response and response.status_code != 200:
        color_print(f"✗ EROARE: Categoria cu ID {category_id} nu există.", 'error')
        return
    
    name = color_input("Nume produs: ")
    if not name:
        color_print("✗ EROARE: Numele produsului nu poate fi gol.", 'error')
        return
    
    try:
        price = float(color_input("Preț produs (MDL): "))
        if price <= 0:
            color_print("✗ EROARE: Prețul trebuie să fie pozitiv.", 'error')
            return
    except ValueError:
        color_print("✗ EROARE: Prețul trebuie să fie un număr valid.", 'error')
        return
    
    description = color_input("Descriere produs (opțional): ")
    
    try:
        stock = int(color_input("Stoc produs (opțional, default 0): ") or "0")
        if stock < 0:
            color_print("✗ EROARE: Stocul nu poate fi negativ.", 'error')
            return
    except ValueError:
        stock = 0
    
    product_data = {
        'name': name,
        'price': price,
        'description': description,
        'stock': stock,
        'category_id': int(category_id)
    }
    
    response = make_request('POST', '/products', product_data)
    
    if response and response.status_code == 201:
        product = response.json()
        color_print("✓ Produsul a fost creat cu succes!", 'success')
        print_result("ID", product.get('id', 'N/A'))
        print_result("Nume", product.get('name', 'N/A'))
        print_result("Preț", f"{product.get('price', 'N/A')} MDL")
        print_result("Stoc", product.get('stock', 'N/A'))
        print_result("Categorie", product.get('category_id', 'N/A'))
    
    elif response:
        color_print(f"✗ EROARE: {response.status_code} - {response.text}", 'error')

def configure_server():
    """Configurează URL-ul serverului."""
    global BASE_URL
    
    print_section("⚙️ CONFIGURARE SERVER")
    
    current_url = BASE_URL
    color_print(f"URL curent: {current_url}", 'info')
    
    new_url = color_input("Introdu URL-ul nou al serverului: ")
    
    if new_url:
        BASE_URL = new_url
        color_print(f"✓ URL-ul serverului a fost schimbat la: {BASE_URL}", 'success')
        
        # Testăm conexiunea
        color_print("🔍 Testare conexiune...", 'info')
        response = make_request('GET', '/categories')
        
        if response and response.status_code == 200:
            color_print("✓ Conexiune reușită!", 'success')
        else:
            color_print("⚠️ Conexiune eșuată. Verifică URL-ul și dacă serverul rulează.", 'warning')
    else:
        color_print("ℹ  URL-ul nu a fost modificat.", 'warning')

def main():
    """Funcția principală."""
    
    print_header("🛒 MAGAZIN ONLINE - CLIENT HTTP")
    color_print("📝 Aplicație pentru gestionarea magazinului online via API HTTP", 'info')
    color_print("🔍 Asigură-te că serverul API rulează înainte de a continua.", 'warning')
    
    while True:
        try:
            show_main_menu()
            choice = color_input("\nAlege o opțiune: ")
            
            if choice == '1':
                # Meniu categorii
                while True:
                    show_category_menu()
                    cat_choice = color_input("\nAlege o opțiune: ")
                    
                    if cat_choice == '1':
                        list_categories()
                    elif cat_choice == '2':
                        get_category_details()
                    elif cat_choice == '3':
                        create_category()
                    elif cat_choice == '4':
                        update_category()
                    elif cat_choice == '5':
                        delete_category()
                    elif cat_choice == '6':
                        break
                    else:
                        color_print("✗ EROARE: Opțiune invalidă!", 'error')
            
            elif choice == '2':
                # Meniu produse
                while True:
                    show_product_menu()
                    prod_choice = color_input("\nAlege o opțiune: ")
                    
                    if prod_choice == '1':
                        list_products_in_category()
                    elif prod_choice == '2':
                        create_product()
                    elif prod_choice == '3':
                        break
                    else:
                        color_print("✗ EROARE: Opțiune invalidă!", 'error')
            
            elif choice == '3':
                configure_server()
            
            elif choice == '4':
                color_print("👋 La revedere!", 'success')
                break
            
            else:
                color_print("✗ EROARE: Opțiune invalidă!", 'error')
        
        except KeyboardInterrupt:
            color_print("\n👋 La revedere!", 'success')
            break
        except EOFError:
            color_print("\n👋 La revedere!", 'success')
            break

if __name__ == "__main__":
    main()
