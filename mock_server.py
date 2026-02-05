#!/usr/bin/env python3
"""
Server HTTP mock pentru testarea clientului de magazin online
Radează pe http://localhost:8000
"""

from flask import Flask, jsonify, request
from datetime import datetime

app = Flask(__name__)

# Date de test
categories = [
    {
        "id": 1,
        "title": "Electronice",
        "description": "Produse electronice și gadget-uri",
        "created_at": "2024-01-01T10:00:00Z",
        "updated_at": "2024-01-01T10:00:00Z"
    },
    {
        "id": 2,
        "title": "Carti",
        "description": "Carti si materiale de lectura",
        "created_at": "2024-01-02T11:00:00Z",
        "updated_at": "2024-01-02T11:00:00Z"
    },
    {
        "id": 3,
        "title": "Imbracaminte",
        "description": "Haine si accesorii",
        "created_at": "2024-01-03T12:00:00Z",
        "updated_at": "2024-01-03T12:00:00Z"
    }
]

products = [
    {
        "id": 1,
        "name": "Laptop Dell XPS",
        "price": 15000.00,
        "description": "Laptop performant pentru lucru",
        "stock": 5,
        "category_id": 1
    },
    {
        "id": 2,
        "name": "Smartphone iPhone",
        "price": 12000.00,
        "description": "Telefon mobil de ultima generatie",
        "stock": 10,
        "category_id": 1
    },
    {
        "id": 3,
        "name": "Programare Python",
        "price": 150.00,
        "description": "Carte despre programare in Python",
        "stock": 20,
        "category_id": 2
    },
    {
        "id": 4,
        "name": "Tricou Cotton",
        "price": 120.00,
        "description": "Tricou din bumbac 100%",
        "stock": 50,
        "category_id": 3
    }
]

next_category_id = 4
next_product_id = 5

@app.route('/api/categories', methods=['GET'])
def get_categories():
    return jsonify(categories)

@app.route('/api/categories/<int:category_id>', methods=['GET'])
def get_category(category_id):
    category = next((c for c in categories if c['id'] == category_id), None)
    if not category:
        return jsonify({"error": "Categoria nu exista"}), 404
    
    # Adaugă produsele din această categorie
    category_products = [p for p in products if p['category_id'] == category_id]
    category_with_products = category.copy()
    category_with_products['products'] = category_products
    
    return jsonify(category_with_products)

@app.route('/api/categories', methods=['POST'])
def create_category():
    global next_category_id
    
    data = request.get_json()
    if not data or 'title' not in data:
        return jsonify({"error": "Titlul este obligatoriu"}), 400
    
    new_category = {
        "id": next_category_id,
        "title": data['title'],
        "description": data.get('description', ''),
        "created_at": datetime.now().isoformat() + 'Z',
        "updated_at": datetime.now().isoformat() + 'Z'
    }
    
    categories.append(new_category)
    next_category_id += 1
    
    return jsonify(new_category), 201

@app.route('/api/categories/<int:category_id>', methods=['PUT'])
def update_category(category_id):
    category = next((c for c in categories if c['id'] == category_id), None)
    if not category:
        return jsonify({"error": "Categoria nu exista"}), 404
    
    data = request.get_json()
    if not data:
        return jsonify({"error": "Date invalide"}), 400
    
    if 'title' in data:
        category['title'] = data['title']
    if 'description' in data:
        category['description'] = data['description']
    
    category['updated_at'] = datetime.now().isoformat() + 'Z'
    
    return jsonify(category)

@app.route('/api/categories/<int:category_id>', methods=['DELETE'])
def delete_category(category_id):
    global categories
    
    category = next((c for c in categories if c['id'] == category_id), None)
    if not category:
        return jsonify({"error": "Categoria nu exista"}), 404
    
    categories = [c for c in categories if c['id'] != category_id]
    
    return jsonify({"message": "Categoria a fost stearsa"})

@app.route('/api/categories/<int:category_id>/products', methods=['GET'])
def get_products_by_category(category_id):
    category = next((c for c in categories if c['id'] == category_id), None)
    if not category:
        return jsonify({"error": "Categoria nu exista"}), 404
    
    category_products = [p for p in products if p['category_id'] == category_id]
    return jsonify(category_products)

@app.route('/api/products', methods=['POST'])
def create_product():
    global next_product_id
    
    data = request.get_json()
    if not data or not all(k in data for k in ['name', 'price', 'category_id']):
        return jsonify({"error": "Numele, pretul si categoria sunt obligatorii"}), 400
    
    # Verifică dacă există categoria
    category = next((c for c in categories if c['id'] == data['category_id']), None)
    if not category:
        return jsonify({"error": "Categoria specificata nu exista"}), 400
    
    new_product = {
        "id": next_product_id,
        "name": data['name'],
        "price": float(data['price']),
        "description": data.get('description', ''),
        "stock": data.get('stock', 0),
        "category_id": data['category_id']
    }
    
    products.append(new_product)
    next_product_id += 1
    
    return jsonify(new_product), 201

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({"status": "OK", "timestamp": datetime.now().isoformat() + 'Z'})

if __name__ == '__main__':
    print("🚀 Server mock pornit pe http://localhost:8000")
    print("📋 API endpoints disponibile:")
    print("   GET    /api/categories")
    print("   GET    /api/categories/{id}")
    print("   POST   /api/categories")
    print("   PUT    /api/categories/{id}")
    print("   DELETE /api/categories/{id}")
    print("   GET    /api/categories/{id}/products")
    print("   POST   /api/products")
    print("   GET    /api/health")
    print("\n🛒 Foloseste clientul shop_client.py pentru a testa!")
    
    app.run(host='0.0.0.0', port=8000, debug=True)
