# LL4 - Client HTTP pentru Magazin Online

## Descriere
Aplicație de consolă pentru comunicarea cu un magazin online via API HTTP.

## Funcționalități

### 📂 Categorii (CRUD complet)
- ✅ **Listează toate categoriile** - Afișează lista de categorii disponibile
- ✅ **Vezi detalii categorie** - Afișează informații complete despre o categorie
- ✅ **Creează categorie nouă** - Adaugă o categorie nouă în magazin
- ✅ **Modifică categorie** - Actualizează titlul și descrierea unei categorii
- ✅ **Șterge categorie** - Elimină o categorie din magazin

### 📦 Produse
- ✅ **Listează produsele dintr-o categorie** - Afișează produsele dintr-o categorie specifică
- ✅ **Creează produs nou** - Adaugă un produs nou într-o categorie

## Instalare și Rulare




### Dependințe
```bash
pip install requests
```

### Rulare
```bash
cd /Users/mood_buster/pr/LL4
python3 shop_client.py
```

## Configurare Server

Aplicația se conectează implicit la: `http://localhost:8000/api`

Poți schimba URL-ul serverului din meniul principal (opțiunea 3).

## API Endpoints Utilizate

### Categorii
- `GET /api/categories` - Listează toate categoriile
- `GET /api/categories/{id}` - Detalii categorie
- `POST /api/categories` - Creează categorie nouă
- `PUT /api/categories/{id}` - Modifică categorie
- `DELETE /api/categories/{id}` - Șterge categorie

### Produse
- `GET /api/categories/{id}/products` - Produse dintr-o categorie
- `POST /api/products` - Creează produs nou

## Structură Date

### Categorie
```json
{
  "id": 1,
  "title": "Electronice",
  "description": "Produse electronice",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

### Produs
```json
{
  "id": 1,
  "name": "Laptop",
  "price": 15000.00,
  "description": "Laptop performant",
  "stock": 10,
  "category_id": 1
}
```

## Exemple de Utilizare

1. **Pornire aplicație:**
   ```bash
   python3 shop_client.py
   ```

2. **Navigare meniu:**
   - Alege `1` pentru Gestionare Categorii
   - Alege `2` pentru Gestionare Produse
   - Alege `3` pentru Configurare Server

3. **Creează categorie:**
   - Meniu Categorii → `3` (Creează categorie nouă)
   - Introdu titlu și descriere

4. **Creează produs:**
   - Meniu Produse → `2` (Creează produs nou)
   - Introdu ID categorie, nume, preț, etc.

## Caracteristici

- 🎨 **Interfață colorată** - Culori pentru diferite tipuri de mesaje
- 📱 **Meniuri interactive** - Navigare ușoară prin opțiuni
- ✅ **Validare date** - Verificare input utilizator
- 🔄 **Gestionare erori** - Mesaje clare pentru erori de rețea
- ⚙️ **Configurare flexibilă** - Schimbare URL server

## Note

- Asigură-te că serverul API rulează înainte de a porni clientul
- Aplicația folosește cereri HTTP standard (GET, POST, PUT, DELETE)
- Toate datele sunt trimise în format JSON
- Timeout-ul pentru cereri este setat implicit de biblioteca `requests`
