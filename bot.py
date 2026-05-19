import logging
import os
from PIL import Image
import io
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes

# Token du bot
TOKEN = "8816501367:AAEs73CUKH5YVD8YnQWLpwaIV-FsIu3wa70"

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def add_watermark(photo_bytes: bytes) -> bytes:
    # Ouvrir la photo
    photo = Image.open(io.BytesIO(photo_bytes)).convert("RGBA")
    
    # Ouvrir le logo
    logo = Image.open("logo.png").convert("RGBA")
    
    # Taille du logo = 20% de la largeur de la photo
    photo_width, photo_height = photo.size
    logo_width = int(photo_width * 0.20)
    ratio = logo_width / logo.width
    logo_height = int(logo.height * ratio)
    logo = logo.resize((logo_width, logo_height), Image.LANCZOS)
    
    # Transparence 60%
    r, g, b, a = logo.split()
    a = a.point(lambda x: int(x * 0.6))
    logo.putalpha(a)
    
    # Position bas à droite avec marge de 10px
    margin = 10
    x = photo_width - logo_width - margin
    y = photo_height - logo_height - margin
    
    # Coller le logo
    photo.paste(logo, (x, y), logo)
    
    # Convertir en JPEG
    output = io.BytesIO()
    photo.convert("RGB").save(output, format="JPEG", quality=95)
    return output.getvalue()

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Récupérer toutes les photos envoyées
    photos = update.message.photo
    if photos:
        # Prendre la meilleure qualité
        photo_file = await context.bot.get_file(photos[-1].file_id)
        photo_bytes = await photo_file.download_as_bytearray()
        
        # Ajouter filigrane
        watermarked = add_watermark(bytes(photo_bytes))
        
        # Renvoyer la photo
        await update.message.reply_photo(
            photo=io.BytesIO(watermarked),
            caption="✅ Photo avec filigrane ASBL Ça Pourra"
        )

async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Gérer les photos envoyées comme fichier (sans compression)
    doc = update.message.document
    if doc and doc.mime_type and doc.mime_type.startswith("image/"):
        photo_file = await context.bot.get_file(doc.file_id)
        photo_bytes = await photo_file.download_as_bytearray()
        
        watermarked = add_watermark(bytes(photo_bytes))
        
        await update.message.reply_photo(
            photo=io.BytesIO(watermarked),
            caption="✅ Photo avec filigrane ASBL Ça Pourra"
        )

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.add_handler(MessageHandler(filters.Document.IMAGE, handle_document))
    app.run_polling()

if __name__ == "__main__":
    main()
