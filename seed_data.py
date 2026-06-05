import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app.database import Database, Product, Customer
import random

def random_phone():
    prefixes = ["06", "07", "05"]
    return f"+212 {random.choice(prefixes)}{random.randint(0,9)}{random.randint(0,9)}{random.randint(0,9)}{random.randint(0,9)}{random.randint(0,9)}{random.randint(0,9)}{random.randint(0,9)}{random.randint(0,9)}"

def random_email(name):
    domains = ["gmail.com", "hotmail.com", "outlook.com", "company.ma", "menara.ma", "iam.ma"]
    clean = name.lower().replace(" ", ".").replace("-", ".").replace("'", "")
    return f"{clean}{random.randint(1,999)}@{random.choice(domains)}"

def random_ice():
    return f"{random.randint(1000000000000000, 9999999999999999)}"

def random_address(city):
    streets = [
        "Av. Mohammed V", "Av. Hassan II", "Rue de la Liberté", "Bd. Zerktouni",
        "Rue Oued El Makhazine", "Av. des FAR", "Bd. Mohamed VI", "Rue Atlas",
        "Av. Moulay Ismail", "Rue Ibn Sina", "Bd. Al Massira", "Av. Allal El Fassi",
        "Rue Abou Bakr El Kadiri", "Av. Abdelkrim El Khattabi", "Rue Moulay Rachid",
        "Bd. Al Qods", "Av. Al Mouqawama", "Rue Al Qalâa", "Av. Al Arsa",
        "Rue Al Alam"
    ]
    nums = f"N°{random.randint(1, 300)}, {random.choice(['Appt', 'Étage', 'Imm.'])} {random.randint(1, 50)}"
    return f"{nums}, {random.choice(streets)}, {city}"

MOROCCAN_CITIES = [
    "Casablanca", "Rabat", "Marrakech", "Fès", "Tanger", "Agadir",
    "Meknès", "Oujda", "Kénitra", "Tétouan", "Safi", "Mohammedia",
    "El Jadida", "Beni Mellal", "Nador", "Taza", "Settat", "Larache",
    "Ksar El Kebir", "Al Hoceima", "Guelmim", "Dakhla", "Laâyoune",
    "Berrechid", "Skhirat", "Témara", "Salé", "Ifrane", "Essaouira"
]

# --- PRODUCTS ---
product_categories = {
    "Huile d'olive": {"prices": [45, 60, 80, 120, 150], "unit": "L", "package": "Bouteille"},
    "Couscous": {"prices": [15, 22, 30, 45], "unit": "kg", "package": "Sachet"},
    "Tagine en terre cuite": {"prices": [120, 180, 250, 350, 500], "unit": "piece", "package": "Carton"},
    "Thé à la menthe": {"prices": [25, 40, 60, 85], "unit": "kg", "package": "Boîte"},
    "Pâtisserie marocaine": {"prices": [80, 120, 180, 250, 350], "unit": "kg", "package": "Boîte"},
    "Jus d'orange frais": {"prices": [12, 18, 25, 35], "unit": "L", "package": "Bouteille"},
    "Amandes": {"prices": [60, 90, 130, 180], "unit": "kg", "package": "Sachet"},
    "Miel pur": {"prices": [80, 120, 180, 250], "unit": "kg", "package": "Pot"},
    "Huile d'argan": {"prices": [150, 250, 350, 500], "unit": "L", "package": "Bouteille"},
    "Dattes Medjoul": {"prices": [90, 140, 200, 280], "unit": "kg", "package": "Barquette"},
    "Savon noir": {"prices": [25, 35, 50, 70], "unit": "piece", "package": "Pot"},
    "Ghassoul": {"prices": [30, 45, 60, 90], "unit": "kg", "package": "Sachet"},
    "Babouche en cuir": {"prices": [120, 180, 250, 350], "unit": "piece", "package": "Paire"},
    "Caftan traditionnel": {"prices": [800, 1200, 2000, 3500, 5000], "unit": "piece", "package": "Carton"},
    "Bougie artisanale": {"prices": [20, 35, 50, 80], "unit": "piece", "package": "Boîte"},
    "Zellige (carreau)": {"prices": [25, 40, 60, 90], "unit": "piece", "package": "Carton"},
    "Tapis berbère": {"prices": [500, 1200, 2500, 5000, 8000], "unit": "piece", "package": "Rouleau"},
    "Plateau en cuivre": {"prices": [150, 250, 400, 600], "unit": "piece", "package": "Carton"},
    "Lampadaire en fer forgé": {"prices": [300, 500, 800, 1200], "unit": "piece", "package": "Carton"},
    "Porte-clés artisanal": {"prices": [15, 25, 40, 60], "unit": "piece", "package": "Lot"},
    "T-shirt en coton": {"prices": [80, 120, 180, 250], "unit": "piece", "package": "Carton"},
    "Djellaba homme": {"prices": [250, 400, 600, 900], "unit": "piece", "package": "Carton"},
    "Djellaba femme": {"prices": [300, 450, 700, 1000], "unit": "piece", "package": "Carton"},
    "Chèche en laine": {"prices": [60, 90, 140, 200], "unit": "piece", "package": "Lot"},
    "Bonnet en laine": {"prices": [40, 60, 90, 130], "unit": "piece", "package": "Lot"},
    "Huile de ricin": {"prices": [35, 50, 75, 100], "unit": "L", "package": "Bouteille"},
    "Eau de rose": {"prices": [20, 30, 45, 65], "unit": "L", "package": "Flacon"},
    "Eau de fleur d'oranger": {"prices": [25, 35, 55, 80], "unit": "L", "package": "Flacon"},
    "Kohl (khôl)": {"prices": [15, 25, 40, 60], "unit": "piece", "package": "Boîte"},
    "Henna": {"prices": [10, 18, 30, 50], "unit": "kg", "package": "Sachet"},
    "Savon au lait d'ânesse": {"prices": [20, 30, 45, 65], "unit": "piece", "package": "Savon"},
    "Crème hydratante": {"prices": [45, 70, 110, 160], "unit": "piece", "package": "Pot"},
    "Shampoing solide": {"prices": [30, 45, 65, 90], "unit": "piece", "package": "Savon"},
    "Lentilles": {"prices": [12, 18, 25, 35], "unit": "kg", "package": "Sachet"},
    "Pois chiches": {"prices": [14, 20, 28, 40], "unit": "kg", "package": "Sachet"},
    "Haricots blancs": {"prices": [13, 19, 26, 38], "unit": "kg", "package": "Sachet"},
    "Riz basmati": {"prices": [18, 25, 35, 50], "unit": "kg", "package": "Sachet"},
    "Semoule fine": {"prices": [10, 15, 22, 32], "unit": "kg", "package": "Sachet"},
    "Farine de blé": {"prices": [8, 12, 18, 25], "unit": "kg", "package": "Sachet"},
    "Sucre en poudre": {"prices": [7, 11, 16, 22], "unit": "kg", "package": "Sachet"},
    "Café moulu": {"prices": [40, 60, 85, 120], "unit": "kg", "package": "Paquet"},
    "Lait en poudre": {"prices": [25, 35, 50, 70], "unit": "kg", "package": "Boîte"},
    "Beurre de ferme": {"prices": [30, 45, 65, 90], "unit": "kg", "package": "Barquette"},
    "Fromage râpé": {"prices": [40, 60, 85, 120], "unit": "kg", "package": "Sachet"},
    "Thon en boîte": {"prices": [12, 18, 25, 35], "unit": "piece", "package": "Boîte"},
    "Sardines en boîte": {"prices": [8, 12, 18, 25], "unit": "piece", "package": "Boîte"},
    "Confiture de figues": {"prices": [25, 35, 50, 70], "unit": "kg", "package": "Pot"},
    "Confiture de fraises": {"prices": [22, 32, 45, 65], "unit": "kg", "package": "Pot"},
    "Concentré de tomate": {"prices": [10, 15, 22, 32], "unit": "kg", "package": "Boîte"},
    "Vinaigre de cidre": {"prices": [15, 22, 32, 45], "unit": "L", "package": "Bouteille"},
    "Eau minérale (1.5L)": {"prices": [5, 7, 10, 14], "unit": "piece", "package": "Bouteille"},
    "Soda (Canette)": {"prices": [4, 6, 8, 12], "unit": "piece", "package": "Canette"},
    "Jus multifruits": {"prices": [12, 18, 25, 35], "unit": "L", "package": "Brique"},
    "Lait frais (1L)": {"prices": [8, 12, 16, 22], "unit": "L", "package": "Brique"},
    "Yaourt nature": {"prices": [3, 5, 7, 10], "unit": "piece", "package": "Lot"},
    "Pain de mie": {"prices": [10, 15, 20, 28], "unit": "piece", "package": "Sachet"},
    "Biscuits secs": {"prices": [15, 22, 30, 42], "unit": "kg", "package": "Paquet"},
    "Chocolat noir": {"prices": [25, 35, 50, 70], "unit": "piece", "package": "Tablette"},
    "Cahier 100 pages": {"prices": [5, 8, 12, 18], "unit": "piece", "package": "Lot"},
    "Stylo bille": {"prices": [3, 5, 8, 12], "unit": "piece", "package": "Boîte"},
    "Classeur": {"prices": [8, 12, 18, 25], "unit": "piece", "package": "Carton"},
    "Ramette papier A4": {"prices": [45, 60, 80, 110], "unit": "piece", "package": "Ramette"},
    "Enveloppe": {"prices": [2, 4, 6, 9], "unit": "piece", "package": "Lot"},
    "Feutre marqueur": {"prices": [4, 7, 10, 15], "unit": "piece", "package": "Boîte"},
    "Colle blanche": {"prices": [6, 10, 15, 22], "unit": "piece", "package": "Tube"},
    "Ruban adhésif": {"prices": [5, 8, 12, 18], "unit": "piece", "package": "Rouleau"},
    "Ciseaux": {"prices": [8, 12, 18, 25], "unit": "piece", "package": "Lot"},
    "Chargeur téléphone": {"prices": [25, 40, 60, 90], "unit": "piece", "package": "Boîte"},
    "Câble USB": {"prices": [15, 25, 35, 50], "unit": "piece", "package": "Sachet"},
    "Écouteurs": {"prices": [30, 50, 80, 120], "unit": "piece", "package": "Boîte"},
    "Coque téléphone": {"prices": [20, 35, 50, 80], "unit": "piece", "package": "Sachet"},
    "Clavier USB": {"prices": [60, 90, 140, 200], "unit": "piece", "package": "Boîte"},
    "Souris optique": {"prices": [40, 65, 100, 150], "unit": "piece", "package": "Boîte"},
    "Disque dur externe": {"prices": [300, 500, 800, 1200], "unit": "piece", "package": "Boîte"},
    "Clé USB 32GB": {"prices": [50, 80, 120, 180], "unit": "piece", "package": "Blister"},
    "Ampoule LED": {"prices": [8, 14, 22, 32], "unit": "piece", "package": "Boîte"},
    "Pile AAA": {"prices": [5, 8, 12, 18], "unit": "piece", "package": "Lot"},
    "Filtre à eau": {"prices": [60, 90, 130, 180], "unit": "piece", "package": "Boîte"},
    "Brosse à dents": {"prices": [8, 12, 18, 25], "unit": "piece", "package": "Blister"},
    "Dentifrice": {"prices": [10, 16, 24, 35], "unit": "piece", "package": "Tube"},
    "Savon de toilette": {"prices": [5, 8, 12, 18], "unit": "piece", "package": "Savon"},
    "Shampoing": {"prices": [15, 25, 38, 55], "unit": "L", "package": "Flacon"},
    "Déodorant": {"prices": [12, 18, 28, 40], "unit": "piece", "package": "Aérosol"},
    "Papier toilette": {"prices": [12, 18, 25, 35], "unit": "piece", "package": "Lot"},
    "Mouchoirs en boîte": {"prices": [8, 12, 18, 25], "unit": "piece", "package": "Boîte"},
    "Lessive liquide": {"prices": [30, 45, 65, 90], "unit": "L", "package": "Bouteille"},
    "Eau de javel": {"prices": [8, 12, 18, 25], "unit": "L", "package": "Bouteille"},
    "Détergent sol": {"prices": [15, 22, 32, 45], "unit": "L", "package": "Bouteille"},
    "Liquide vaisselle": {"prices": [10, 16, 24, 35], "unit": "L", "package": "Bouteille"},
    "Éponge": {"prices": [3, 5, 8, 12], "unit": "piece", "package": "Lot"},
    "Sac poubelle": {"prices": [8, 12, 18, 25], "unit": "piece", "package": "Rouleau"},
    "Aluminium ménager": {"prices": [10, 15, 22, 30], "unit": "piece", "package": "Rouleau"},
    "Film alimentaire": {"prices": [8, 12, 18, 25], "unit": "piece", "package": "Rouleau"},
    "Bouilloire électrique": {"prices": [120, 200, 300, 450], "unit": "piece", "package": "Carton"},
    "Fer à repasser": {"prices": [150, 250, 400, 600], "unit": "piece", "package": "Carton"},
    "Grille-pain": {"prices": [100, 180, 280, 400], "unit": "piece", "package": "Carton"},
    "Mixeur plongeant": {"prices": [80, 140, 220, 350], "unit": "piece", "package": "Carton"},
    "Balance de cuisine": {"prices": [60, 100, 160, 250], "unit": "piece", "package": "Carton"},
}

# --- CUSTOMERS ---
first_names_m = [
    "Mohamed", "Ahmed", "Hassan", "Omar", "Ali", "Youssef", "Khalid", "Karim", "Abdellah", "Driss",
    "Said", "Rachid", "Noureddine", "Mourad", "Hicham", "Tarik", "Mehdi", "Yassine", "Amine", "Soufiane",
    "Adil", "Jamal", "Fouad", "Redouane", "Brahim", "Ismail", "Zakaria", "Anas", "Hamza", "Ayoub",
    "Abdelkader", "Abderrahim", "Lhoucine", "Mustapha", "Larbi", "Mbarek", "Abdelmajid", "Abdelouahab", "Abdessamad", "Abdelaziz",
    "Moulay", "Mounir", "Fahd", "Jawad", "Badr", "Ilyas", "Younes", "Marouane", "Walid", "Loubna"
]

first_names_f = [
    "Fatima", "Amina", "Khadija", "Zineb", "Najat", "Samira", "Nadia", "Sanaa", "Hind", "Imane",
    "Sara", "Meryem", "Asmae", "Souad", "Hafida", "Keltoum", "Latifa", "Naima", "Fatima-Zahra", "Malika",
    "Rachida", "Saida", "Karima", "Halima", "Yasmina", "Ghizlane", "Oumaima", "Chaimae", "Salma", "Wafaa",
    "Soukaina", "Hajar", "Kawtar", "Lamiaa", "Khaoula", "Mouna", "Nawal", "Rania", "Hanane", "Nabila",
    "Ilham", "Bouchra", "Narjiss", "Touria", "Jamila", "Mina", "Aicha", "Rabea", "Houria", "Zahra"
]

last_names = [
    "El Amrani", "Benali", "El Fassi", "Alaoui", "Idrissi", "El Ouafi", "Bennani", "El Khatib",
    "El Gharbaoui", "Tazi", "Berrada", "El Malki", "Sabri", "El Kadiri", "El Bakkali",
    "El Haddad", "El Bouazzaoui", "El Rhazi", "El Aroussi", "Cherkaoui", "Moujahid",
    "El Mansouri", "El Ammari", "El Kettani", "El Hamdaoui", "El Abbassi", "El Idrissi",
    "Ouazzani", "El Filali", "Bouzoubaa", "El Azhari", "El Maadi", "Belkadi", "El Haouari",
    "El Bourkadi", "El Yaakoubi", "El Makkaoui", "El Moussaoui", "El Alami", "El Othmani",
    "El Khyari", "El Hamri", "El Gueddari", "El Hariri", "El Amri", "El Bazi", "El Arbaoui",
    "El Kaddouri", "El Midaoui", "El Hachimi"
]

company_names = [
    "Atlanta Import", "Maroc Produits", "Al Janoub Distribution", "Fès Délices", "Tanger Commerce",
    "Agadir Bio", "Sahara Logistique", "Atlas Fournitures", "Rif Équipement", "Gharb Agro",
    "Orient Luxe", "Maghreb Textile", "Méditerranée Shipping", "Saiss Industrie", "Draâ Matériaux",
    "Tensift Services", "Laâyoune Express", "Dakhla Pêche", "Moulouya Agricole", "Ziz Artisanat",
    "Hespérides Distribution", "Toubkal Électronique", "Anti-Atlas Mines", "Mamora Bois",
    "Sebou Transport", "Bouregreg Pharma", "Oum Errabia Agro", "Souss Fruits", "Dadès Voyages",
    "Haouz Construction", "Tafilalet Textile", "Rhamna Métallurgie", "Chaouia Chimie",
    "Doukkala Laiterie", "Abda Huiles", "Ahmar Énergie", "Ghmour Art", "Zemmour Élevage",
    "Ferkla Hydraulique", "Todgha Tourisme", "Cèdre Menuiserie", "Moulay Idriss Tissu",
    "Youssoufia Pharma", "Béni Mellal Agro", "Khouribga Mines", "El Jadida Maritime",
    "Nador Logistique", "Oujda Commerce", "Settat Industrie", "Taza Bois"
]

def generate_customers(n=100):
    customers = []
    half = n // 2

    # Private individuals (first 50)
    for _ in range(half):
            gender = random.choice(["M", "F"])
            if gender == "M":
                first = random.choice(first_names_m)
            else:
                first = random.choice(first_names_f)
            last = random.choice(last_names)
            name = f"{first} {last}"
            city = random.choice(MOROCCAN_CITIES)
            addr = random_address(city)
            phone = random_phone()
            email = random_email(f"{first}.{last}")
            tax_id = random_ice()
            customers.append(Customer(name=name, address=addr, phone=phone, email=email, tax_id=tax_id))

    # Companies (next 50)
    for name in random.sample(company_names, 50):
            city = random.choice(MOROCCAN_CITIES)
            addr = f"{random.randint(1, 500)}, {random.choice(['Bd.', 'Av.', 'Rue'])} {random.choice(['Mohamed VI', 'Hassan II', 'des FAR', 'Al Massira', 'Moulay Ismail', 'Allal El Fassi', 'Abdelkrim El Khattabi', 'Ibn Sina', 'Oued El Makhazine', 'Al Qods'])}, {city}"
            phone = random_phone()
            email = random_email(name)
            tax_id = random_ice()
            customers.append(Customer(name=name, address=addr, phone=phone, email=email, tax_id=tax_id))

    return customers

def generate_products():
    products = []
    used_names = set()

    for base_name, info in product_categories.items():
        variants = [
            f"{base_name} - Éco",
            f"{base_name} - Standard",
            f"{base_name} - Premium",
            f"{base_name} - Grand format",
        ]
        for i, variant in enumerate(variants):
            if variant in used_names:
                continue
            used_names.add(variant)
            price = random.choice(info["prices"])
            qty = random.randint(10, 500)
            ref = f"REF-{random.randint(10000, 99999)}"
            products.append(Product(
                name=variant,
                description=f"{variant} de haute qualité",
                reference=ref,
                unit_price=float(price),
                quantity=qty,
                unit=info["unit"],
                package_type=info["package"]
            ))

    # Shuffle and take 100
    random.shuffle(products)
    return products[:100]


def main():
    db = Database()
    import shutil

    # --- Wipe existing products & customers ---
    cursor = db.conn.cursor()
    cursor.execute("DELETE FROM products")
    cursor.execute("DELETE FROM customers")
    db.conn.commit()

    products = generate_products()
    for i, p in enumerate(products, 1):
        db.insert_product(p)
        if i % 25 == 0:
            print(f"  Inserted {i}/100 products")

    customers = generate_customers(100)
    for i, c in enumerate(customers, 1):
        db.insert_customer(c)
        if i % 25 == 0:
            print(f"  Inserted {i}/100 customers")

    db.close()
    print(f"\nDone! {len(products)} products and {len(customers)} customers inserted into minvoice.db")


if __name__ == "__main__":
    main()
