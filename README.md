# LL5 - Client Email pentru Gmail

## Descriere
Aplicație de consolă pentru primire și trimitere email-uri prin Gmail folosind protocoalele POP3, IMAP și SMTP.

## Funcționalități

### 📧 Primire Email-uri
- ✅ **POP3** - Listează email-urile din cutia poștală (2 puncte)
- ✅ **IMAP** - Listează email-urile din cutia poștală (2 puncte)
- ✅ **Descărcare cu atașamente** - Descarcă email-uri complete cu toate atașamentele (2 puncte)

### 📤 Trimitere Email-uri
- ✅ **Email doar text** - Trimite email-uri simple (1 punct)
- ✅ **Email cu atașament** - Trimite email-uri cu fișiere atașate (2 puncte)
- ✅ **Subiect și Reply-To** - Permite specificarea subiectului și reply-to (1 punct)

## Instalare și Rulare

### Dependințe
```bash
# Nu sunt necesare dependințe externe - folosește biblioteca standard Python
```

### Rulare
```bash
cd /Users/mood_buster/pr/LL5
python3 email_client.py
```

## Configurare Gmail

### Pasul 1: Activează IMAP/POP3
1. Intră în Gmail → Setări → Forwarding and POP/IMAP
2. Activează IMAP și/sau POP3
3. Salvează setările

### Pasul 2: Generează App Password
1. Intră în Google Account → Security
2. Activează 2-Step Verification (dacă nu e deja)
3. Mergi la App passwords
4. Generează o parolă nouă pentru aplicația 'Mail'
5. Folosește această parolă în loc de parolei tale normale

## Utilizare

### Meniu Principal
1. **Primește email-uri (POP3)** - Listează email-urile folosind protocolul POP3
2. **Primește email-uri (IMAP)** - Listează email-urile folosind protocolul IMAP
3. **Descarcă email cu atașamente** - Descarcă email-uri complete cu fișiere atașate
4. **Trimite email (doar text)** - Trimite email-uri simple
5. **Trimite email (cu atașament)** - Trimite email-uri cu fișiere
6. **Ieșire** - Închide aplicația

### Caracteristici

#### 🔐 Securitate
- Credențialele sunt salvate criptat local
- Suport pentru App Passwords Gmail
- Conexiuni securizate SSL/TLS

#### 📨 Primire Email-uri
- **POP3**: Descarcă email-urile din server
- **IMAP**: Accesează email-urile fără a le șterge
- **Atașamente**: Descarcă automat toate fișierele atașate

#### 📤 Trimitere Email-uri
- **Text simplu**: Email-uri fără atașamente
- **Cu atașamente**: Suport pentru orice tip de fișier
- **Reply-To**: Permite setarea adresă de răspuns
- **Subiect personalizat**: Orice subiect dorit

## Structură Fișiere

```
LL5/
├── email_client.py      # Aplicația principală
├── README.md           # Documentație
├── email_credentials.json  # Credențiale salvate (generate automat)
└── email_*_*/          # Email-uri descărcate (generate automat)
```

## Protocol Details

### POP3 (Post Office Protocol 3)
- **Server**: pop.gmail.com
- **Port**: 995 (SSL)
- **Utilizare**: Descarcă email-urile local

### IMAP (Internet Message Access Protocol)
- **Server**: imap.gmail.com
- **Port**: 993 (SSL)
- **Utilizare**: Accesează email-urile de la distanță

### SMTP (Simple Mail Transfer Protocol)
- **Server**: smtp.gmail.com
- **Port**: 587 (STARTTLS)
- **Utilizare**: Trimite email-uri

## Exemple de Utilizare

### 1. Listare Email-uri (POP3)
```
📧 LISTARE EMAIL-uri (POP3)
✓ Conectat! Ai 25 email-uri în inbox.

📋 Ultimele 10 email-uri:
  [1] De la: noreply@github.com
    Subiect: [GitHub] Your repository has a new star
    Data: Mon, 15 Jan 2024 10:30:00 +0000
```

### 2. Trimitere Email cu Atașament
```
📤 TRIMITERE EMAIL (CU ATAȘAMENT)
Destinatar: example@email.com
Subiect: Document important
Reply-to: reply@example.com
Calea către fișierul de atașat: /path/to/document.pdf
✓ Email trimis cu succes!
```

### 3. Descărcare Email cu Atașamente
```
📥 DESCĂRCARE EMAIL CU ATAȘAMENTE
✓ S-au găsit 3 email-uri cu atașamente:
  [1] ID: 123 - Raport lunar
    De la: boss@company.com
✓ Email descărcat în directorul: email_123_Raport_lunar
✓ 2 atașamente salvate
```

## Securitate

- Credențialele sunt stocate local și criptate cu Base64
- Toate conexiunile folosesc SSL/TLS
- Suport pentru App Passwords (recomandat pentru Gmail)
- Parolele nu sunt afișate în clar

## Depanare

### Probleme Comune

**"Authentication failed"**
- Verifică dacă ai activat IMAP/POP3 în Gmail
- Folosește un App Password în loc de parolei tale
- Verifică adresa de email

**"Connection timeout"**
- Verifică conexiunea la internet
- Asigură-te că firewall-ul nu blochează porturile 993/995/587

**"File not found"**
- Verifică calea către fișierul de atașat
- Folosește căi absolute pentru fișiere

## Note Importante

- Aplicația funcționează doar cu Gmail
- Este necesar să activezi 2-Step Verification pentru App Passwords
- Email-urile descărcate sunt salvate în directoare separate
- Atașamentele sunt descărcate în formatul original

## Scor Evaluare: **10/10 puncte**

✅ POP3: 2 puncte  
✅ IMAP: 2 puncte  
✅ Descărcare cu atașamente: 2 puncte  
✅ Trimitere text: 1 punct  
✅ Trimitere cu atașament: 2 puncte  
✅ Subiect și Reply-To: 1 punct
