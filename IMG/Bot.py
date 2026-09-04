from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ParseMode
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext 
import time
import os
from dotenv import load_dotenv
import psycopg2
from urllib.parse import urlparse
import time


import psycopg2
from urllib.parse import urlparse

# Fonction pour se connecter à la base de données
def connect_db():
    url = os.getenv('DATABASE_URL')
    if url is None:
        raise ValueError("DATABASE_URL not found in environment variables")

    result = urlparse(url)
    db_name = result.path[1:]  # Enlève le premier caractère '/'
    db_user = result.username
    db_password = result.password
    db_host = result.hostname
    db_port = result.port

    return psycopg2.connect(
        database=db_name,
        user=db_user,
        password=db_password,
        host=db_host,
        port=db_port
    )

def create_table():
    conn = connect_db()
    cursor = conn.cursor()

    # Création de la table users si elle n'existe pas
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            user_id VARCHAR(255) UNIQUE NOT NULL
        )
    ''')
    conn.commit()
    cursor.close()
    conn.close()

# Charger les variables d'environnement depuis le fichier .env
load_dotenv()

# Récupérer le token à partir de l'environnement
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Chemin de base du projet
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # Chemin du dossier où se trouve le script



def save_user(user_id):
    conn = connect_db()
    cursor = conn.cursor()

    try:
        cursor.execute('INSERT INTO users (user_id) VALUES (%s) ON CONFLICT (user_id) DO NOTHING', (user_id,))
        conn.commit()
        print(f"Utilisateur {user_id} enregistré.")
    except Exception as e:
        print(f"Erreur lors de l'enregistrement de l'utilisateur : {e}")
    finally:
        cursor.close()
        conn.close()



def start(update: Update, context: CallbackContext):
    create_table()  # Crée la table si elle n'existe pas
    user_id = str(update.effective_user.id)
    user_name = update.effective_user.first_name  # Récupération du prénom de l'utilisateur
    save_user(user_id)  # Enregistrer l'utilisateur


    # Chemin complet vers l'image
    image_path = os.path.join(BASE_DIR, 'images', 'LOGO.JPG')
    
    # Envoi de l'image avant le texte et les boutons
    context.bot.send_photo(chat_id=update.effective_chat.id, photo=open(image_path, 'rb'))
    
    # Configuration des boutons
    keyboard = [
        [InlineKeyboardButton("ℹ️ Informations", callback_data='informations'),
         InlineKeyboardButton("📱 Contact", callback_data='contact')],
        [InlineKeyboardButton("📋 Menu DR SPEED", callback_data='menu')],
        [
            InlineKeyboardButton("Instagram", url='https://www.instagram.com/drspeednord?igsh=Y2R4emtqZjR0anFr&utm_source=qr'),
            InlineKeyboardButton("Potato", url='https://ymd168.org/joinchat/hICGKwu1zJpffaC0-ylPUQ'),
            InlineKeyboardButton("Canal", url='https://t.me/THEDRSPEEDNO')
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Envoi du texte avec les boutons
    update.message.reply_text(
         f'*🩺 DR SPEED BOT*\n\n_Bienvenu(e), {user_name} !_\n\n'
        '_ENVOYER /Start au bot pour le garder à jour !_\n\n'
        '_Utilise les boutons ci-dessous pour naviguer dans les menus 👇_', 
        reply_markup=reply_markup,
        parse_mode='Markdown'
        
    )


def get_users():
    conn = connect_db()
    cursor = conn.cursor()
    user_ids = []

    try:
        cursor.execute('SELECT user_id FROM users')
        user_ids = [row[0] for row in cursor.fetchall()]  # Récupère tous les user_id dans une liste
    except Exception as e:
        print(f"Erreur lors de la récupération des utilisateurs : {e}")
    finally:
        cursor.close()
        conn.close()
    
    return user_ids

def notify(update: Update, context: CallbackContext):
    # Vérifie que l'utilisateur est un admin
    if update.effective_user.id not in [1333584617]:  # Remplace par ton ID
        update.message.reply_text("Seuls les administrateurs peuvent envoyer des notifications.")
        return

    # Définir un mode test (par exemple, ajouter "test" dans la commande)
    test_mode = False
    if len(context.args) > 0 and context.args[0].lower() == "test":
        test_mode = True

    # Récupère les utilisateurs
    users = get_users()
    if test_mode:
        users = [1333584617]  # Remplace par ton propre ID pour le test

    if not users:
        update.message.reply_text("Aucun utilisateur à notifier.")
        return

    # Préparer le message
    message = " ".join(context.args[1:]) if test_mode else " ".join(context.args)
    if not message:
        update.message.reply_text("Veuillez fournir un message à envoyer.")
        return

    # Variables de contrôle
    delay = 2
    batch_size = 30
    long_pause = 120

    # Envoi des messages
    for i, user_id in enumerate(users):
        try:
            context.bot.send_message(chat_id=user_id, text=message, parse_mode=ParseMode.MARKDOWN)
            print(f"Message envoyé à {user_id}")
        except Exception as e:
            print(f"Erreur lors de l'envoi à {user_id}: {e}")
        time.sleep(delay)

        if (i + 1) % batch_size == 0:
            print(f"Pause prolongée après {batch_size} messages.")
            time.sleep(long_pause)

    # Confirmation à l'admin
    update.message.reply_text(f"Message envoyé à {'1 utilisateur (test)' if test_mode else f'{len(users)} utilisateurs'}.")




# Dictionnaire des variétés pour chaque produit avec des chemins relatifs

VARIETIES_EGGS_FROZEN= {
   'CALI PLATE DRYSIFT 🏆🌋🔥': {
        'media': {
            'video': os.path.join(BASE_DIR, 'images', 'IMG_8860.MOV'),
        },
        'description': (
            "*CALI PLATE DRYSIFT 🏆🌋🔥*\n"
            "GLASSY OU MUTER 🥶\n"
            "FILM 🎥 🍿\n\n"
            "1️⃣ _AnimalFace 🦋🍰_\n"
            "2️⃣ _GushMints 🍵🍃_\n"
            "3️⃣ _Tangie ☀️🍊_\n"
            "4️⃣ _Apple Fritter 🍎🍏_\n"
            "5️⃣ _Pink Runtz 🌸🌺_\n"
            "6️⃣ _Runtz ⛽️🔥_\n\n"
            "_5gr: 120€_\n"
            "_10gr: 220€_\n"
            "_20gr: 400€_\n"
            "_50gr: 850€_\n"
            "_100gr: 1650€_\n"
            "_200gr: 3200€+_\n\n"
            "+ 📱"
        )
    }
}
VARIETIES_CALI_BRAND= {
   'Grape BubbleGum 🍇🍭': {
        'media': {
            'video': os.path.join(BASE_DIR, 'images', 'IMG_9179.MOV'),
        },
        'description': (
            "*GOLDEN STATE 🏆🇺🇸 FOLIE🔥*\n"
            "10/10 MEILLEUR PRIX\n\n"
            "1️⃣ _Grape BubbleGum 🍇🍭_\n\n"
            "_7g: 120€_\n"
            "_14g: 220€_\n"
            "_28g: 360€_\n"
            "_56gr: 620€_\n"
            "_112gr: 1200€_\n"
            "_224gr: 2300€_\n"
            "_448gr: 4500€_\n\n"
            "+ 📱"
        )
    },
    'G41 🍨🍊': {
        'media': {
            'video': os.path.join(BASE_DIR, 'images', 'IMG_9178.MOV'),
        },
        'description': (
            "*GOLDEN STATE 🏆🇺🇸 FOLIE🔥*\n"
            "10/10 MEILLEUR PRIX\n\n"
            "2️⃣ _G41 🍨🍊_\n\n"
            "_7g: 120€_\n"
            "_14g: 220€_\n"
            "_28g: 360€_\n"
            "_56gr: 620€_\n"
            "_112gr: 1200€_\n"
            "_224gr: 2300€_\n"
            "_448gr: 4500€_\n\n"
            "+ 📱"
        )
    },
    'Girl Scout Cookies 🍬🍪': {
        'media': {
            'video': os.path.join(BASE_DIR, 'images', 'IMG_9177.MOV'),
        },
        'description': (
            "*GOLDEN STATE 🏆🇺🇸 FOLIE🔥*\n"
            "10/10 MEILLEUR PRIX\n\n"
            "3️⃣ _Girl Scout Cookies 🍬🍪_\n\n"
            "_7g: 120€_\n"
            "_14g: 220€_\n"
            "_28g: 360€_\n"
            "_56gr: 620€_\n"
            "_112gr: 1200€_\n"
            "_224gr: 2300€_\n"
            "_448gr: 4500€_\n\n"
            "+ 📱"
        )
    },
    'Gushers 🍭🍬': {
        'media': {
            'video': os.path.join(BASE_DIR, 'images', 'IMG_9181.MOV'),
        },
        'description': (
            "*GOLDEN STATE 🏆🇺🇸 FOLIE🔥*\n"
            "10/10 MEILLEUR PRIX\n\n"
            "4️⃣ _Gushers 🍭🍬_\n\n"
            "_7g: 120€_\n"
            "_14g: 220€_\n"
            "_28g: 360€_\n"
            "_56gr: 620€_\n"
            "_112gr: 1200€_\n"
            "_224gr: 2300€_\n"
            "_448gr: 4500€_\n\n"
            "+ 📱"
        )
    }
}
VARIETIES_TOP_SHELF= {
   'Kabosu Zozi 🍋‍🟩🍋🍬': {
        'media': {
            'video': os.path.join(BASE_DIR, 'images', 'IMG_8848.MOV'),
        },
        'description': (
            "*THE TENCO 🏆⭐️*\n"
            "1️⃣ _Kabosu Zozi 🍋‍🟩🍋🍬_\n\n"
            "_1Pot(3,5g): 110€_\n"
            "_2Pot(7g): 200€_\n"
            "_4Pot(14g): 380€_\n"
            "_8Pot(28g): 700€_\n"
            "_16Pot(56g): 1300€_\n"
            "_32Pot(112g): 2500€_\n\n"
            "+ 📱💲💲💲"
        )
    },
    'Alaskan Crab Legs 🦀🍱🍭': {
        'media': {
            'video': os.path.join(BASE_DIR, 'images', 'IMG_8849.MOV'),
        },
        'description': (
            "*THE TENCO 🏆⭐️*\n"
            "2️⃣ _Alaskan Crab Legs 🦀🍱🍭_\n\n"
            "_1Pot(3,5g): 110€_\n"
            "_2Pot(7g): 200€_\n"
            "_4Pot(14g): 380€_\n"
            "_8Pot(28g): 700€_\n"
            "_16Pot(56g): 1300€_\n"
            "_32Pot(112g): 2500€_\n\n"
            "+ 📱💲💲💲"
        )
    }
}
VARIETIES_FROZEN_120u = {
  'Gelato 41 🍧🍨': {
        'media': {
            'video': os.path.join(BASE_DIR, 'images', 'IMG_9321.MOV'),
        },
        'description': (
            "*TOP CALI AAA 🇺🇸*\n"
            "1️⃣ _Gelato 41 🍧🍨_\n\n"
            "_10gr: 130€_\n"
            "_25gr: 250€_\n"
            "_50gr: 400€_\n"
            "_100gr: 700€_\n"
            "_200gr: 1450€_\n"
            "_500gr: 3000€_\n"
            "_1klg: 5800€+_\n\n"
            "+ 📱"
        )
    },
    'Envy Fire 🍬🔥': {
        'media': {
            'video': os.path.join(BASE_DIR, 'images', 'IMG_9322.MOV'),
        },
        'description': (
            "*TOP CALI AAA 🇺🇸*\n"
            "2️⃣ _Envy Fire 🍬🔥_\n\n"
            "_10gr: 130€_\n"
            "_25gr: 250€_\n"
            "_50gr: 400€_\n"
            "_100gr: 700€_\n"
            "_200gr: 1450€_\n"
            "_500gr: 3000€_\n"
            "_1klg: 5800€+_\n\n"
            "+ 📱"
        )
    },
    'Permanent X Zkittlez ⛽️🌈': {
        'media': {
            'video': os.path.join(BASE_DIR, 'images', 'IMG_9323.MOV'),
        },
        'description': (
            "*TOP CALI AAA 🇺🇸*\n"
            "3️⃣ _Permanent X Zkittlez ⛽️🌈_\n\n"
            "_10gr: 130€_\n"
            "_25gr: 250€_\n"
            "_50gr: 400€_\n"
            "_100gr: 700€_\n"
            "_200gr: 1450€_\n"
            "_500gr: 3000€_\n"
            "_1klg: 5800€+_\n\n"
            "+ 📱"
        )
    },
    'Air Heads 🌸💨': {
        'media': {
            'video': os.path.join(BASE_DIR, 'images', 'IMG_9326.MOV'),
        },
        'description': (
            "*TOP CALI AAA 🇺🇸*\n"
            "4️⃣ _Air Heads 🌸💨_\n\n"
            "_10gr: 130€_\n"
            "_25gr: 250€_\n"
            "_50gr: 400€_\n"
            "_100gr: 700€_\n"
            "_200gr: 1450€_\n"
            "_500gr: 3000€_\n"
            "_1klg: 5800€+_\n\n"
            "+ 📱"
        )
    },
    'Black Scotti ⚫️🥖': {
        'media': {
            'video': os.path.join(BASE_DIR, 'images', 'IMG_9331.MOV'),
        },
        'description': (
            "*TOP CALI AAA 🇺🇸*\n"
            "5️⃣ _Black Scotti ⚫️🥖_\n\n"
            "_10gr: 130€_\n"
            "_25gr: 250€_\n"
            "_50gr: 400€_\n"
            "_100gr: 700€_\n"
            "_200gr: 1450€_\n"
            "_500gr: 3000€_\n"
            "_1klg: 5800€+_\n\n"
            "+ 📱"
        )
    }
}
VARIETIES_KG= {
    
   'SAHA TERPS STATIC 🏆': {
        'media': {
            'video': os.path.join(BASE_DIR, 'images', 'IMG_8864.MOV'),
        },
        'description': (
            "*SAHA TERPS STATIC 🏆*\n"
            "GLASSY OU MUTER 🥶\n"
            "ON VOIT TOUT EN UNE SEULE VIDÉO\n\n"
            "1️⃣ _Amaretto ☕️🌰_\n"
            "2️⃣ _Goverment Oasis 🧃🍉_\n"
            "3️⃣ _Guava Ice 🥭🥶_\n"
            "4️⃣ _Yellow Cake 🌈🎂_\n"
            "5️⃣ _Puppy Breath 🍵🍎_\n\n"
            "_5gr: 160€_\n"
            "_10gr: 300€_\n"
            "_20gr: 550€_\n"
            "_50gr: 1050€_\n"
            "_100gr: 2050€_\n"
            "_200gr: 4000€+_\n\n"
            "+ 📱"
        )
    }
}
VARIETIES_KGF= {
    
    
  
    'Tiramisù 🎂🍰': {
        'media': {
            'video': os.path.join(BASE_DIR, 'images', 'IMG_0757.MOV'),
        },
        'description': (
            "*GLASSY OU MUTER 🥶*\n"
            "1️⃣ _Tiramisù 🎂🍰_\n\n"
            "_5Gr: 110€_\n"
            "_10Gr: 200€_\n"
            "_20gr: 380€_\n"
            "_50gr: 700€_\n"
            "_100gr: 1300€_\n"
            "_200gr: 2500€+_\n\n"
            "+ 📱"
        )
    },
    'Lamponį ☀️🍊': {
        'media': {
            'video': os.path.join(BASE_DIR, 'images', 'IMG_0758.MOV'),
        },
        'description': (
            "*GLASSY OU MUTER 🥶*\n"
            "2️⃣  _Lamponį ☀️🍊_\n\n"
            "_5Gr: 110€_\n"
            "_10Gr: 200€_\n"
            "_20gr: 380€_\n"
            "_50gr: 700€_\n"
            "_100gr: 1300€_\n"
            "_200gr: 2500€+_\n\n"
            "+ 📱"
        )
    }
}
VARIETIES_BAD= {
    

    'Tangiebert 🍒🍊': {
        'media': {
            'video': os.path.join(BASE_DIR, 'images', '8504773328308233820.MP4'),
        },
        'description': (
            "*GLASSY OU MUTER 🥶*\n"
            "1️⃣  _Tangiebert 🍒🍊_\n\n"
            "_5gr: 100€_\n"
            "_10gr: 190€_\n"
            "_20gr: 360€_\n"
            "_50gr: 700€_\n"
            "_100gr: 1350€_\n"
            "_200gr: 2600€+_\n\n"
            "+ 📱"
        )
    }
}
VARIETIES_ICE= {
    
     'SAHA TERPS STATIC 🏆': {
        'media': {
            'video': os.path.join(BASE_DIR, 'images', 'IMG_8865.MOV'),
        },
        'description': (
            "*SAHA TERPS STATIC 🏆*\n"
            "PREMIUM ⚡️⭐️🇺🇸\n"
            "GLASSY OU MUTER 🥶\n"
            "ON VOIT TOUT EN UNE SEULE VIDÉO\n\n"
            "1️⃣ _Cereal Milk 🥛🌾_\n"
            "2️⃣ _Peach Limeade 🍑🍋‍🟩_\n"
            "3️⃣ _Orange Candy 🍊🌈_\n\n"
            "_5gr: 180€_\n"
            "_10gr: 350€_\n"
            "_20gr: 650€_\n"
            "_50gr: 1200€_\n"
            "_100gr: 2200€_\n"
            "_200gr: 4200€+_\n\n"
            "+ 📱"
        )
    }
}
VARIETIES_GAZ= {
     'Tropicana 🌴🍍': {
        'media': {
            'video': os.path.join(BASE_DIR, 'images', 'IMG_8496.MOV'),
        },
        'description': (
            "*CALI PLATE FROZEN PREMIUM 🏆*\n"
            "GLASSY OU MUTER 🥶\n\n"
            "1️⃣ _Tropicana 🌴🍍_\n\n"
            "_5gr: 150€_\n"
            "_10gr: 280€_\n"
            "_20gr: 540€_\n"
            "_50gr: 1050€_\n"
            "_100gr: 2050€_\n"
            "_200gr: 4000€+_\n\n"
            "+ 📱"
        )
    },
    'WhiteRuntz 🧯🍬': {
        'media': {
            'video': os.path.join(BASE_DIR, 'images', 'IMG_8497.MOV'),
        },
        'description': (
            "*CALI PLATE FROZEN PREMIUM 🏆*\n"
            "GLASSY OU MUTER 🥶\n\n"
            "2️⃣ _WhiteRuntz 🧯🍬_\n\n"
            "_5gr: 150€_\n"
            "_10gr: 280€_\n"
            "_20gr: 540€_\n"
            "_50gr: 1050€_\n"
            "_100gr: 2050€_\n"
            "_200gr: 4000€+_\n\n"
            "+ 📱"
        )
    },
    'SunsetSherbet ☀️🍊': {
        'media': {
            'video': os.path.join(BASE_DIR, 'images', 'IMG_8498.MOV'),
        },
        'description': (
            "*CALI PLATE FROZEN PREMIUM 🏆*\n"
            "GLASSY OU MUTER 🥶\n\n"
            "3️⃣ _SunsetSherbet ☀️🍊_\n\n"
            "_5gr: 150€_\n"
            "_10gr: 280€_\n"
            "_20gr: 540€_\n"
            "_50gr: 1050€_\n"
            "_100gr: 2050€_\n"
            "_200gr: 4000€+_\n\n"
            "+ 📱"
        )
    }
}
VARIETIES_EGGS = {
    'TropicThunder 🌴🍍': {
        'media': {
            'video': os.path.join(BASE_DIR, 'images', 'IMG_3900.MOV'),
        },
        'description': (
            "*🩺 DR SPEED BOT*\n"
            "*FRESH FROZEN ICE´O´LATOR 🧊*\n"
            "*PLAKET28,5Gr 🇺🇸*\n\n"
            "1️⃣ _TropicThunder 🌴🍍_\n\n"
            "_2,5gr: 160€_\n"
            "_5gr: 300€_\n"
            "_10gr: 550€_\n"
            "_28,5gr: 1400€+_\n\n"
            "+ 📱"
        )
    },
    'PinkLimez 🌸🍋': {
        'media': {
            'video': os.path.join(BASE_DIR, 'images', 'IMG_3897.MOV'),
        },
        'description': (
            "*🩺 DR SPEED BOT*\n"
            "*FRESH FROZEN ICE´O´LATOR 🧊*\n"
            "*PLAKET28,5Gr 🇺🇸*\n\n"
            "2️⃣ _PinkLimez 🌸🍋_\n\n"
            "_2,5gr: 160€_\n"
            "_5gr: 300€_\n"
            "_10gr: 550€_\n"
            "_28,5gr: 1400€+_\n\n"
            "+ 📱"
        )
    },
    'SlurppyValley 🍭🍬': {
        'media': {
            'video': os.path.join(BASE_DIR, 'images', 'IMG_3896.MOV'),
        },
        'description': (
            "*🩺 DR SPEED BOT*\n"
            "*FRESH FROZEN ICE´O´LATOR 🧊*\n"
            "*PLAKET28,5Gr 🇺🇸*\n\n"
            "3️⃣ _SlurppyValley 🍭🍬_\n\n"
            "_2,5gr: 160€_\n"
            "_5gr: 300€_\n"
            "_10gr: 550€_\n"
            "_28,5gr: 1400€+_\n\n"
            "+ 📱"
        )
    }
}



# Variables globales
current_variety = {}
image_messages = {}




def button(update: Update, context):
    query = update.callback_query
    query.answer()

    if query.data.startswith('photo_video_'):
        show_photo_video_menu(query, context)

    elif query.data == 'next_variety':
        chat_id = query.message.chat_id
        if chat_id in current_variety:
            product, index = current_variety[chat_id]
            # Détermine les clés de variétés en fonction du produit
            if product == 'eggs_frozen':
                variety_keys = list(VARIETIES_EGGS_FROZEN.keys())
            
            elif product == 'cali_brand':
                variety_keys = list(VARIETIES_CALI_BRAND.keys())
            
            elif product == 'top_shelf':
                variety_keys = list(VARIETIES_TOP_SHELF.keys())

            
            elif product == 'frozen_120u':
                variety_keys = list(VARIETIES_FROZEN_120u.keys())
            
            elif product == 'kg':
                variety_keys = list(VARIETIES_KG.keys())
            
            elif product == 'kgf':
                variety_keys = list(VARIETIES_KGF.keys())
            
            elif product == 'bad':
                variety_keys = list(VARIETIES_BAD.keys())

            elif product == 'ice':
                variety_keys = list(VARIETIES_ICE.keys())
            
            elif product == 'gaz':
                variety_keys = list(VARIETIES_GAZ.keys())

            elif product == 'eggs':
                variety_keys = list(VARIETIES_EGGS.keys())
            

                


            else:
                print("Unknown product category.")
                return

            # Incrémentation de l'index et mise à jour
            index = (index + 1) % len(variety_keys)
            current_variety[chat_id] = (product, index)
            show_photo_video_menu(query, context)
        else:
            print("No current variety set for this chat.")
    
    elif query.data == 'informations':
        show_information_menu(query)

    elif query.data == 'contact':
        delete_image_messages(query.message.chat_id, context)
        show_contact_menu(query)

    elif query.data == 'menu':
        show_cali_rabbit_menu(query)

     
    elif query.data == 'eggs_frozen':
        show_eggs_frozen_menu(query)
    
    elif query.data == 'cali_brand':
        show_cali_brand_menu(query)
    
    elif query.data == 'top_shelf':
        show_top_shelf_menu(query)

    
    
    elif query.data == 'frozen_120u':
        show_frozen_120u_menu(query)
    
    elif query.data == 'kg':
        show_kg_menu(query)
    
    elif query.data == 'kgf':
        show_kgf_menu(query)
    
    elif query.data == 'bad':
        show_bad_menu(query)

    elif query.data == 'ice':
        show_ice_menu(query)

    elif query.data == 'gaz':
        show_gaz_menu(query)

    elif query.data == 'eggs':
        show_eggs_menu(query)








    elif query.data == 'livraison':
        show_livraison_menu(query)

    elif query.data == 'postal':
        show_postal_menu(query)

    elif query.data == 'retour_main_menu':
        show_main_menu(query)

    elif query.data == 'retour_photo_video':
        delete_image_messages(query.message.chat_id, context)
        show_cali_rabbit_menu(query)


def delete_image_messages(chat_id, context):
    for msg_id in image_messages.get(chat_id, []):
        try:
            context.bot.delete_message(chat_id=chat_id, message_id=msg_id)
        except Exception as e:
            print(f"Erreur lors de la suppression du message : {e}")
    image_messages[chat_id] = []

def show_photo_video_menu(query, context):
    chat_id = query.message.chat_id

    # Vérifie si le chat_id a une variété actuelle
    if chat_id not in current_variety:
        print("No current variety set for this chat.")
        return

    product, index = current_variety[chat_id]

    # Sélection des variétés en fonction du produit
    if product == 'eggs_frozen':
       varieties = VARIETIES_EGGS_FROZEN
    
    elif product == 'cali_brand':  # Ajout de la nouvelle catégorie
        varieties = VARIETIES_CALI_BRAND
    
    elif product == 'top_shelf':  # Ajout de la nouvelle catégorie
        varieties = VARIETIES_TOP_SHELF

   
    elif product == 'frozen_120u':  # Ajout de la nouvelle catégorie
        varieties = VARIETIES_FROZEN_120u

  
    elif product == 'kg':  # Ajout de la nouvelle catégorie
        varieties = VARIETIES_KG
    
    elif product == 'kgf':  # Ajout de la nouvelle catégorie
        varieties = VARIETIES_KGF
    
    elif product == 'bad':  # Ajout de la nouvelle catégorie
        varieties = VARIETIES_BAD

    elif product == 'ice':  # Ajout de la nouvelle catégorie
        varieties = VARIETIES_ICE

    elif product == 'gaz':  # Ajout de la nouvelle catégorie
        varieties = VARIETIES_GAZ
    
    elif product == 'eggs':  # Ajout de la nouvelle catégorie
        varieties = VARIETIES_EGGS




  



  


  


 
    else:
        print("Unknown product category.")
        return

    variety_keys = list(varieties.keys())

    # Vérification de l'index
    if index >= len(variety_keys):
        print("Index out of range for varieties.")
        return

    variety_key = variety_keys[index]
    variety = varieties[variety_key]

    delete_image_messages(chat_id, context)  # Suppression des messages d'image précédents

    media = variety['media']

    # Envoie de vidéo ou d'image
    if 'video' in media:
        media_file = media['video']
        message = context.bot.send_video(
    chat_id=chat_id, 
    video=open(media_file, 'rb'), 
    caption=variety['description'],
    parse_mode='Markdown',
    width=720,   # Largeur en pixels
    height=1280  # Hauteur en pixels
)
    else:
        media_file = media['image']
        message = context.bot.send_photo(
            chat_id=chat_id, 
            photo=open(media_file, 'rb'), 
            caption=variety['description'], 
            parse_mode='Markdown'
        )

    # Ajout de l'ID du message à la liste des messages d'image
    if chat_id not in image_messages:
        image_messages[chat_id] = []
    image_messages[chat_id].append(message.message_id)

    # Créez le clavier avec les options
    keyboard = [
        InlineKeyboardButton("Suivant", callback_data='next_variety'),
        InlineKeyboardButton("Commander", callback_data='contact'),
        InlineKeyboardButton("🔙 Retour", callback_data='retour_photo_video')
    ]

    reply_markup = InlineKeyboardMarkup([keyboard])

    # Efface le message d'origine avant de montrer la photo/vidéo
    context.bot.delete_message(chat_id=chat_id, message_id=query.message.message_id)

    # Ajoute les options sous la photo/vidéo
    context.bot.send_message(chat_id=chat_id, text="_Sélectionnez une option :_", reply_markup=reply_markup, parse_mode='Markdown')









def show_information_menu(query):
    keyboard = [
        [InlineKeyboardButton("🚚 Livraison", callback_data='livraison')],
        [InlineKeyboardButton("📦 Envoi Postal", callback_data='postal')],
        [InlineKeyboardButton("🔙 Retour", callback_data='retour_main_menu')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(text="_Quelles informations cherchez-vous ?_", reply_markup=reply_markup, parse_mode='Markdown')

def show_contact_menu(query):
    contact_text = (
    "*🩺 DR SPEED BOT*\n"
    "└─Contacts\n\n"
    "*Envoi Postal :📮*\n"
    "└ \\@Drspeednord\_Envoi\n\n"  # Échappez le @
    "*Livraison :🏎️*\n"
    "└ \\@drspeednord1\n\n"        # Échappez le @
    "*SAV/GROSSECOMMANDE:*\n"
    "└ \\@drspeednordthc"          # Échappez le @
)

    keyboard = [
        [InlineKeyboardButton("Envoi Postal", url="https://t.me/Drspeednord_Envoi")],
        [InlineKeyboardButton("Livraison", url="https://t.me/drspeednord1")],
        [InlineKeyboardButton("🔙 Retour", callback_data='retour_main_menu')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(text=contact_text, reply_markup=reply_markup, parse_mode='Markdown')

def show_livraison_menu(query):
    livraison_text = (
        "🩺 *DR SPEED BOT*\n"
        "ℹ️ *INFORMATIONS LIVRAISON*\n\n"
        "_Pour passer une commande, contactez_ [@DrSpeednord1]\n\n"
        "📍 *Livraison 59/62 🏎️*\n"
        "└ _Minimum de commande : 150€_\n"
        "*SAV/GROSSECOMMANDE*: [@Drspeednordthc]"
    )
    keyboard = [
        [InlineKeyboardButton("🔙 Retour", callback_data='retour_main_menu')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(text=livraison_text, reply_markup=reply_markup, parse_mode='Markdown')

def show_postal_menu(query):
    postal_text = (
        "🩺 *DR SPEED BOT*\n"
        "ℹ️ *INFORMATIONS ENVOI POSTAL*\n\n"
        "_Pour passer une commande, contactez_ [@Drspeednord_Envoi]\n\n"
        "*CONDITION D’ENVOIS* \n\n"
        "_Les commandes sont expédiées 24h après la prise de commande_ \n\n"
        "*JOURS D'ENVOIS*\n\n" 
        "_Lundi, mardi, mercredi, jeudi et vendredi_\n\n"
        "*FRAIS D’ENVOIS*\n\n"
        "_✉️ Lettre suivi ou Mondial Relay 48-72h avec suivi_\n\n"
        "└ _vers la France : 10€_ \n\n"
        "└ _vers l’international : 30€_\n\n"
        " *PAIEMENT *\n\n"
        "└ _Cryptomonnaies_\n\n"






    )
    keyboard = [
        [InlineKeyboardButton("📦 Envoi Postal", callback_data='postal')],
        [InlineKeyboardButton("🚚 Livraison", callback_data='livraison')],
        [InlineKeyboardButton("🔙 Retour", callback_data='retour_main_menu')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(text=postal_text, reply_markup=reply_markup, parse_mode='Markdown')

def show_main_menu(query):
    keyboard = [
        [InlineKeyboardButton("ℹ️ Informations", callback_data='informations'),
         InlineKeyboardButton("📱 Contact", callback_data='contact')],
        [InlineKeyboardButton("📋 Menu DR SPEED", callback_data='menu')],
          [
            InlineKeyboardButton("Instagram", url='https://www.instagram.com/drspeednord?igsh=Y2R4emtqZjR0anFr&utm_source=qr'),
            InlineKeyboardButton("Potato", url='https://ymd168.org/joinchat/hICGKwu1zJpffaC0-ylPUQ'),
            InlineKeyboardButton("Canal", url='https://t.me/THEDRSPEEDNO')
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(
    text='*🩺 DR SPEED BOT*\n\n__ENVOYER /Start au bot pour le garder à jour !__\n\n_Utilises les boutons ci-dessous pour naviguer dans les menus 👇_', 
    reply_markup=reply_markup, 
    parse_mode='Markdown'
)    
    



def show_cali_rabbit_menu(query):
    keyboard = [



 [InlineKeyboardButton("TOP CALI AAA 🏆⭐️🇺🇸", callback_data='frozen_120u')],
 #[InlineKeyboardButton("TOP SHELF US 🏆🇺🇸⭐️", callback_data='cali_brand')],
 #[InlineKeyboardButton("CALI THE TENCO BOÎTE 3,5🏆🗃️🇺🇸", callback_data='top_shelf')],
 #[InlineKeyboardButton("CALI PLATE FROZEN 🏆🇺🇸🧊", callback_data='gaz')],
#  [InlineKeyboardButton("CALI PLATE DRYSIFT 🏆🌋🔥", callback_data='eggs_frozen')],
 # [InlineKeyboardButton("SAHA TERPS STATIC 🇺🇸⚡️🆕", callback_data='kg')],




#[InlineKeyboardButton("SAHA TERPS STATIC PREMIUM🇺🇸⚡️🆕", callback_data='ice')],


   #[InlineKeyboardButton("ICE LABZ ICE O LATOR 🏆🧊⭐️", callback_data='eggs')],

 # [InlineKeyboardButton("KGF 120U FROZEN🏆❄️⭐️", callback_data='kgf')],
  # [InlineKeyboardButton("BAD BERRED FROZEN🏆🧊🔥", callback_data='bad')],












        [InlineKeyboardButton("🔙 Retour", callback_data='retour_main_menu')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(text="*🩺 DR SPEED BOT*\n"
    "" , reply_markup=reply_markup, parse_mode='Markdown')






def show_cali_brand_menu(query): 
    chat_id = query.message.chat_id
    current_variety[chat_id] = ('cali_brand', 0)  # Initialisez l'index pour 'cali_brand'
    
    cali_brand_text = (
    "<b>🩺 DR SPEED BOT</b>\n"
    "└─<em>Menu TOP SHELF US</em>\n\n"
    "<b>GOLDEN STATE 🏆🇺🇸 FOLIE🔥</b>\n"
    "<b>10/10 MEILLEUR PRIX</b>\n\n"
    "1️⃣ Grape BubbleGum 🍇🍭\n"
    "2️⃣ G41 🍨🍊\n"
    "3️⃣ Girl Scout Cookies 🍬🍪\n"
    "4️⃣ Gushers 🍭🍬\n\n"
    "<em>7g: 120€</em>\n"
    "<em>14g: 220€</em>\n"
    "<em>28g: 360€</em>\n"
    "<em>56gr: 620€</em>\n"
    "<em>112gr: 1200€</em>\n"
    "<em>224gr: 2300€</em>\n"
    "<em>448gr: 4500€</em>\n\n"
    "<em>+ 📱</em>"
    )
      
    
    options = [
        {'text': 'Photo/Vidéo', 'callback_data': 'photo_video_cali_brand'},
        {'text': 'Commander', 'callback_data': 'contact'}
    ]




    show_menu(query, cali_brand_text, options)
def show_frozen_120u_menu(query):
    chat_id = query.message.chat_id
    current_variety[chat_id] = ('frozen_120u', 0)  # Initialisez l'index pour 'frozen_120u'

    frozen_120u_menu_text = (
 
   
    "<b>🩺 DR SPEED BOT</b>\n"
     "└─<em>Menu TOP CALI AAA</em>\n\n"
    "<b>1000% US 🇺🇸</b>\n"
    "MIEUX QUE CALI NL🇺🇸🇳🇱\n\n"
    "1️⃣ Gelato 41 🍧🍨\n"
    "2️⃣ Envy Fire 🍬🔥\n"
    "3️⃣ Permanent X Zkittlez ⛽️🌈\n"
    "4️⃣ Air Heads 🌸💨\n"
    "5️⃣ Black Scotti ⚫️🥖\n\n"
    "<em>10gr: 130€</em>\n"
    "<em>25gr: 250€</em>\n"
    "<em>50gr: 400€</em>\n"
    "<em>100gr: 700€</em>\n"
    "<em>200gr: 1450€</em>\n"
    "<em>500gr: 3000€</em>\n"
    "<em>1klg: 5800€+</em>\n\n"
    "<em>+ 📱</em>"
    )
    
    options = [
        {'text': 'Photo/Vidéo', 'callback_data': 'photo_video_frozen_120u'},
        {'text': 'Commander', 'callback_data': 'contact'}
    ]
    show_menu(query, frozen_120u_menu_text, options)
def show_top_shelf_menu(query):
    chat_id = query.message.chat_id
    current_variety[chat_id] = ('top_shelf', 0)  # Initialisez l'index pour 'top_shelf'

    top_shelf_menu_text = (
   "<b>🩺 DR SPEED BOT</b>\n"
       "└─<em>Menu Cali Brand</em>\n\n"
    "<b>THE TENCO 🏆⭐️</b>\n"
    "<b>NEW EDITION EXCLU 🆕⭐️</b>\n"
    "<b>BOITE 3,5G 🫙</b>\n\n"
    "1️⃣ Kabosu Zozi 🍋‍🟩🍋🍬\n"
    "2️⃣ Alaskan Crab Legs 🦀🍱🍭\n\n"
    "<em>1Pot(3,5g): 110€</em>\n"
    "<em>2Pot(7g): 200€</em>\n"
    "<em>4Pot(14g): 380€</em>\n"
    "<em>8Pot(28g): 700€</em>\n"
    "<em>16Pot(56g): 1300€</em>\n"
    "<em>32Pot(112g): 2500€</em>\n\n"
    "<em>+ 📱💲💲💲</em>"
) 
    
    options = [
        {'text': 'Photo/Vidéo', 'callback_data': 'photo_video_top_shelf'},
        {'text': 'Commander', 'callback_data': 'contact'}
    ]
    show_menu(query, top_shelf_menu_text, options)
def show_eggs_frozen_menu(query):


    

    
    chat_id = query.message.chat_id
    current_variety[chat_id] = ('eggs_frozen', 0)  # Initialisez l'index pour 'eggs_frozen'

    eggs_frozen_menu_text = (
    "<b>🩺 DR SPEED BOT</b>\n"
     "└─<em>Menu CALI PLATE DRYSIFT</em>\n\n"
    "<b>CALI PLATE DRYSIFT 🏆🌋🔥</b>\n"
    "<b>GLASSY OU MUTER 🥶</b>\n"
    "<b>FILM 🎥 🍿</b>\n\n"
    "1️⃣ AnimalFace 🦋🍰\n"
    "2️⃣ GushMints 🍵🍃\n"
    "3️⃣ Tangie ☀️🍊\n"
    "4️⃣ Apple Fritter 🍎🍏\n"
    "5️⃣ Pink Runtz 🌸🌺\n"
    "6️⃣ Runtz ⛽️🔥\n\n"
    "<em>5gr: 120€</em>\n"
    "<em>10gr: 220€</em>\n"
    "<em>20gr: 400€</em>\n"
    "<em>50gr: 850€</em>\n"
    "<em>100gr: 1650€</em>\n"
    "<em>200gr: 3200€+</em>\n\n"
    "<em>+ 📱</em>"
)
    
    options = [
        {'text': 'Photo/Vidéo', 'callback_data': 'photo_video_eggs_frozen'},
        {'text': 'Commander', 'callback_data': 'contact'}
    ]
    show_menu(query, eggs_frozen_menu_text, options)   
def show_kg_menu(query):

    
    chat_id = query.message.chat_id
    current_variety[chat_id] = ('kg', 0)  # Initialisez l'index pour 'eggs_frozen'

    kg_menu_text = (
     "<b>🩺 DR SPEED BOT</b>\n"
   "└─<em>Menu SAHA TERPS STATIC</em>\n\n"
    "<b>SAHA TERPS STATIC 🏆</b>\n"
    "<b>GLASSY OU MUTER 🥶</b>\n"
    "<b>ON VOIT TOUT EN UNE SEULE VIDÉO</b>\n\n"
    "1️⃣ Amaretto ☕️🌰\n"
    "2️⃣ Goverment Oasis 🧃🍉\n"
    "3️⃣ Guava Ice 🥭🥶\n"
    "4️⃣ Yellow Cake 🌈🎂\n"
    "5️⃣ Puppy Breath 🍵🍎\n\n"
    "<em>5gr: 160€</em>\n"
    "<em>10gr: 300€</em>\n"
    "<em>20gr: 550€</em>\n"
    "<em>50gr: 1050€</em>\n"
    "<em>100gr: 2050€</em>\n"
    "<em>200gr: 4000€+</em>\n\n"
    "<em>+ 📱</em>"
)
    
    options = [
        {'text': 'Photo/Vidéo', 'callback_data': 'photo_video_kg'},
        {'text': 'Commander', 'callback_data': 'contact'}
    ]
    show_menu(query, kg_menu_text, options)   
def show_kgf_menu(query):

    
    chat_id = query.message.chat_id
    current_variety[chat_id] = ('kgf', 0)  # Initialisez l'index pour 'eggs_frozen'

    kgf_menu_text = (
     "<b>🩺 DR SPEED BOT</b>\n"
    "└─<em>Menu KGF 120U FROZEN</em>\n\n"
    "1️⃣  Tiramisù 🎂🍰\n"
    "2️⃣ Lamponi🍊\n\n"
    "<em>5g: 110€</em>\n"
    "<em>10g: 200€</em>\n"
    "<em>20g: 380€</em>\n"
    "<em>50g: 700€</em>\n"
    "<em>100g: 1300€</em>\n"
    "<em>200g: 2500€</em>\n\n"
    "<em>+📱</em>"
)
    
    options = [
        {'text': 'Photo/Vidéo', 'callback_data': 'photo_video_kg'},
        {'text': 'Commander', 'callback_data': 'contact'}
    ]
    show_menu(query, kgf_menu_text, options)   
def show_bad_menu(query):

    
    chat_id = query.message.chat_id
    current_variety[chat_id] = ('bad', 0)  # Initialisez l'index pour 'eggs_frozen'

    bad_menu_text = (
   "<b>🩺 DR SPEED BOT</b>\n"
    "└─<em>Menu BAD BERRED FROZEN</em>\n\n"
    "<b>GLASSY OU MUTER 🥶</b>\n\n"
    "1️⃣ Tangiebert 🍒🍊\n\n"
    "<em>5gr: 100€</em>\n"
    "<em>10gr: 190€</em>\n"
    "<em>20gr: 360€</em>\n"
    "<em>50gr: 700€</em>\n"
    "<em>100gr: 1350€</em>\n"
    "<em>200gr: 2600€+</em>\n\n"
    "+ 📱"
)
    
    options = [
        {'text': 'Photo/Vidéo', 'callback_data': 'photo_video_bad'},
        {'text': 'Commander', 'callback_data': 'contact'}
    ]
    show_menu(query, bad_menu_text, options)   
def show_ice_menu(query):

    
    chat_id = query.message.chat_id
    current_variety[chat_id] = ('ice', 0)  # Initialisez l'index pour 'eggs_frozen'

    ice_menu_text = (
    "<b>🩺 DR SPEED BOT</b>\n"
    "└─<em>Menu SAHA TERPS STATIC</em>\n\n"
    "<b>SAHA TERPS STATIC 🏆</b>\n"
    "<b>PREMIUM ⚡️⭐️🇺🇸</b>\n"
    "<b>GLASSY OU MUTER 🥶</b>\n"
    "<b>ON VOIT TOUT EN UNE SEULE VIDÉO</b>\n\n"
    "1️⃣ Cereal Milk 🥛🌾\n"
    "2️⃣ Peach Limeade 🍑🍋‍🟩\n"
    "3️⃣ Orange Candy 🍊🌈\n\n"
    "<em>5gr: 180€</em>\n"
    "<em>10gr: 350€</em>\n"
    "<em>20gr: 650€</em>\n"
    "<em>50gr: 1200€</em>\n"
    "<em>100gr: 2200€</em>\n"
    "<em>200gr: 4200€+</em>\n\n"
    "<em>+ 📱</em>"
    )
    
    options = [
        {'text': 'Photo/Vidéo', 'callback_data': 'photo_video_ice'},
        {'text': 'Commander', 'callback_data': 'contact'}
    ]
    show_menu(query, ice_menu_text, options)      
def show_gaz_menu(query):

    
    chat_id = query.message.chat_id
    current_variety[chat_id] = ('gaz', 0)  # Initialisez l'index pour 'eggs_frozen'

    gaz_menu_text = (
    "<b>🩺 DR SPEED BOT</b>\n"
    "└─<em>Menu CALI PLATE FROZEN</em>\n\n"
    "<b>CALI PLATE FROZEN PREMIUM 🏆</b>\n"
    "<b>GLASSY OU MUTER 🥶</b>\n\n"
    "1️⃣ Tropicana 🌴🍍\n"
    "2️⃣ WhiteRuntz 🧯🍬\n"
    "3️⃣ SunsetSherbet ☀️🍊\n\n"
    "<em>5gr: 150€</em>\n"
    "<em>10gr: 280€</em>\n"
    "<em>20gr: 540€</em>\n"
    "<em>50gr: 1050€</em>\n"
    "<em>100gr: 2050€</em>\n"
    "<em>200gr: 4000€+</em>\n\n"
    "<em>+ 📱</em>"
)
    
    options = [
        {'text': 'Photo/Vidéo', 'callback_data': 'photo_video_gaz'},
        {'text': 'Commander', 'callback_data': 'contact'}
    ]
    show_menu(query, gaz_menu_text, options)     
def show_eggs_menu(query):

    
    chat_id = query.message.chat_id
    current_variety[chat_id] = ('eggs', 0)  

    eggs_menu_text = (
    "<b>🩺 DR SPEED BOT</b>\n"
    "└─<em>Menu ICE LABZ ICE’O’LATOR</em>\n\n"
    "<b>FRESH FROZEN ICE´O´LATOR 🧊</b>\n"
    "<b>PLAKET28,5Gr 🇺🇸</b>\n\n"
    "1️⃣ TropicThunder 🌴🍍\n"
    "2️⃣ PinkLimez 🌸🍋\n"
    "3️⃣ SlurppyValley 🍭🍬\n\n"
    "<em>2,5gr: 160€</em>\n"
    "<em>5gr: 300€</em>\n"
    "<em>10gr: 550€</em>\n"
    "<em>28,5gr: 1400€+</em>\n\n"
    "<em>+ 📱</em>"
)
    
    options = [
        {'text': 'Photo/Vidéo', 'callback_data': 'photo_video_gaz'},
        {'text': 'Commander', 'callback_data': 'contact'}
    ]
    show_menu(query, eggs_menu_text, options)        




def show_menu(query, text, options):
    keyboard = [InlineKeyboardButton(opt['text'], callback_data=opt['callback_data']) for opt in options]       
    keyboard.append(InlineKeyboardButton("🔙 Retour", callback_data='retour_main_menu'))
    reply_markup = InlineKeyboardMarkup([keyboard])
    query.edit_message_text(text=text, reply_markup=reply_markup, parse_mode='HTML')

  

def main():
    updater = Updater(token=TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    # Commande /start pour démarrer le bot
    dispatcher.add_handler(CommandHandler('start', start))

    # Commande /notify pour envoyer des notifications à tous les utilisateurs enregistrés
    dispatcher.add_handler(CommandHandler('notify', notify))

    dispatcher.add_handler(CallbackQueryHandler(button))  # Assurez-vous que button est défini

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()