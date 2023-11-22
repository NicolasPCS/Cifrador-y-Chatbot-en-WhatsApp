import requests
import sett
import json
import time
import base64
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes

texto_cifrar = ""
clave_cifrar = ""

texto_descifrar = ""
clave_descifrar = ""

listaValsCypher = []
listaValsUncypher = []

def obtener_Mensaje_whatsapp(message):
    if 'type' not in message :
        text = 'mensaje no reconocido'
        return text

    typeMessage = message['type']
    if typeMessage == 'text':
        text = message['text']['body']
    elif typeMessage == 'button':
        text = message['button']['text']
    elif typeMessage == 'interactive' and message['interactive']['type'] == 'list_reply':
        text = message['interactive']['list_reply']['title']
    elif typeMessage == 'interactive' and message['interactive']['type'] == 'button_reply':
        text = message['interactive']['button_reply']['title']
    else:
        text = 'mensaje no procesado'
    
    
    return text

def enviar_Mensaje_whatsapp(data):
    try:
        whatsapp_token = sett.whatsapp_token
        whatsapp_url = sett.whatsapp_url
        headers = {'Content-Type': 'application/json',
                   'Authorization': 'Bearer ' + whatsapp_token}
        print("se envia ", data)
        response = requests.post(whatsapp_url, 
                                 headers=headers, 
                                 data=data)
        
        if response.status_code == 200:
            return 'mensaje enviado', 200
        else:
            return 'error al enviar mensaje', response.status_code
    except Exception as e:
        return e,403
    
def text_Message(number,text):
    data = json.dumps(
            {
                "messaging_product": "whatsapp",    
                "recipient_type": "individual",
                "to": number,
                "type": "text",
                "text": {
                    "body": text
                }
            }
    )
    return data

def text_Message_cifrado(number):
    try:
        vernam = VernamCipherExtended()
        cesar = CifradoCesar()

        partes_texto_a_cifrar = listaValsCypher[0].split("texto:",1)
        partes_clave_a_cifrar = listaValsCypher[1].split("clave:",1)

        text = partes_texto_a_cifrar[1].lstrip()
        key = partes_clave_a_cifrar[1].lstrip()

        print("textoooooo: ", text, "\nkeyyyyyyyyyyyyyyyyyyyyyyyy: ", key)

        cifrado_vernam = vernam.cifrar(text, key)
        cifrado_cesar = cesar.cifrar(cifrado_vernam)

        data = json.dumps(
            {
                "messaging_product": "whatsapp",    
                "recipient_type": "individual",
                "to": number,
                "type": "text",
                "text": {
                    "body": cifrado_cesar
                }
            }
        )
        return data
    except Exception as e:
        print("listavals------",listaValsCypher[0])
        print("listavals.......",listaValsCypher[1])
        print("Error en text_Message_cifrado:", e)
        return f"Error: {e}"

def text_Message_descifrado(number):
    try:
        vernam = VernamCipherExtended()
        cesar = CifradoCesar()

        partes_texto_cifrado = listaValsUncypher[0].split("des_text:",1)
        partes_clave_cifrado = listaValsUncypher[1].split("des_key:",1)

        text = partes_texto_cifrado[1].lstrip()
        key = partes_clave_cifrado[1].lstrip()

        #print("textoooooo: ", text, " keyyyyyyyyyyyyyyyyyyyyyyyy: ", key)

        #descifrado_cesar = cesar.descifrar(listaValsUncypher[0])
        #descifrado_vernam = vernam.descifrar(descifrado_cesar, listaValsUncypher[1])

        descifrado_cesar = cesar.descifrar(text)
        descifrado_vernam = vernam.descifrar(descifrado_cesar, key)

        data = json.dumps(
            {
                "messaging_product": "whatsapp",    
                "recipient_type": "individual",
                "to": number,
                "type": "text",
                "text": {
                    "body": descifrado_vernam
                }
            }
        )
        return data
    except Exception as e:

        partes_texto_cifrado = listaValsUncypher[0].split("des_text:",1)
        partes_clave_cifrado = listaValsUncypher[1].split("des_key:",1)

        text = partes_texto_cifrado[1].lstrip()
        key = partes_clave_cifrado[1].lstrip()

        print("listavals------",text)
        print("listavals.......",key)
        print("Error en text_Message_cifrado:", e)
        return f"Error: {e}"

def buttonReply_Message(number, options, body, footer, sedd,messageId):
    buttons = []
    for i, option in enumerate(options):
        buttons.append(
            {
                "type": "reply",
                "reply": {
                    "id": sedd + "_btn_" + str(i+1),
                    "title": option
                }
            }
        )

    data = json.dumps(
        {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": number,
            "type": "interactive",
            "interactive": {
                "type": "button",
                "body": {
                    "text": body
                },
                "footer": {
                    "text": footer
                },
                "action": {
                    "buttons": buttons
                }
            }
        }
    )
    return data

def listReply_Message(number, options, body, footer, sedd,messageId):
    rows = []
    for i, option in enumerate(options):
        rows.append(
            {
                "id": sedd + "_row_" + str(i+1),
                "title": option,
                "description": ""
            }
        )

    data = json.dumps(
        {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": number,
            "type": "interactive",
            "interactive": {
                "type": "list",
                "body": {
                    "text": body
                },
                "footer": {
                    "text": footer
                },
                "action": {
                    "button": "Ver Opciones",
                    "sections": [
                        {
                            "title": "Secciones",
                            "rows": rows
                        }
                    ]
                }
            }
        }
    )
    return data

def document_Message(number, url, caption, filename):
    data = json.dumps(
        {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": number,
            "type": "document",
            "document": {
                "link": url,
                "caption": caption,
                "filename": filename
            }
        }
    )
    return data

def sticker_Message(number, sticker_id):
    data = json.dumps(
        {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": number,
            "type": "sticker",
            "sticker": {
                "id": sticker_id
            }
        }
    )
    return data

def get_media_id(media_name , media_type):
    media_id = ""
    if media_type == "sticker":
        media_id = sett.stickers.get(media_name, None)
    #elif media_type == "image":
    #    media_id = sett.images.get(media_name, None)
    #elif media_type == "video":
    #    media_id = sett.videos.get(media_name, None)
    #elif media_type == "audio":
    #    media_id = sett.audio.get(media_name, None)
    return media_id

def replyReaction_Message(number, messageId, emoji):
    data = json.dumps(
        {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": number,
            "type": "reaction",
            "reaction": {
                "message_id": messageId,
                "emoji": emoji
            }
        }
    )
    return data

def replyText_Message(number, messageId, text):
    data = json.dumps(
        {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": number,
            "context": { "message_id": messageId },
            "type": "text",
            "text": {
                "body": text
            }
        }
    )
    return data

def markRead_Message(messageId):
    data = json.dumps(
        {
            "messaging_product": "whatsapp",
            "status": "read",
            "message_id":  messageId
        }
    )
    return data

class VernamCipherExtended:
    def __init__(self):
        pass

    @staticmethod
    def _to_binary_string(texto: str) -> str:
        """
        Convierte el texto dado en su representación binaria.
        Cada caracter se representa con 8 bits.
        """
        return ''.join(format(ord(caracter), '08b') for caracter in texto)

    @staticmethod
    def _from_binary_string(cadena_binaria: str) -> str:
        """
        Convierte una cadena binaria en su representación textual.
        Cada conjunto de 8 bits se convierte en un caracter.
        """
        return ''.join(chr(int(cadena_binaria[i:i+8], 2)) for i in range(0, len(cadena_binaria), 8))

    @staticmethod
    def _to_hex(cadena_binaria: str) -> str:
        """
        Convierte una cadena binaria a su representación hexadecimal.
        """
        return hex(int(cadena_binaria, 2))[2:].zfill(len(cadena_binaria) // 4)

    @staticmethod
    def _from_hex(cadena_hex: str) -> str:
        """
        Convierte una cadena hexadecimal a su representación binaria.
        """
        return format(int(cadena_hex, 16), '0' + str(len(cadena_hex) * 4) + 'b')

    def _ajustar_longitud_clave(self, clave: str, longitud_texto: int) -> str:
        """
        Ajusta la longitud de la clave para que coincida con la longitud del texto.
        Si la clave es más corta, se repite. Si es más larga, se trunca.
        """
        return (clave * (longitud_texto // len(clave)) + clave[:longitud_texto % len(clave)])

    def cifrar(self, texto: str, clave: str) -> str:
        """
        Cifra el texto usando una clave y la operación XOR.
        """
        # Asegurarse de que la longitud de la clave coincida con la del texto
        clave_ajustada = self._ajustar_longitud_clave(clave, len(texto))
        
        # Convertir texto y clave a binario
        texto_bin = self._to_binary_string(texto)
        clave_bin = self._to_binary_string(clave_ajustada)

        print(texto_bin)
        print(clave_bin)
        
        # Aplicar XOR entre el texto y la clave
        cifrado_bin = "".join(['1' if t != k else '0' for t, k in zip(texto_bin, clave_bin)])
        
        # Convertir el resultado binario a hexadecimal para que sea imprimible
        return self._to_hex(cifrado_bin)

    def descifrar(self, texto_cifrado_hex: str, clave: str) -> str:
        """
        Descifra el texto cifrado usando la clave y la operación XOR.
        """
        # Convertir el texto cifrado hexadecimal a binario
        texto_cifrado_bin = self._from_hex(texto_cifrado_hex)
        
        # Asegurarse de que la longitud de la clave coincida con la del texto
        clave_ajustada = self._ajustar_longitud_clave(clave, len(texto_cifrado_bin) // 8)

        # Convertir clave a binario
        clave_bin = self._to_binary_string(clave_ajustada)
        
        # Aplicar XOR entre el texto cifrado y la clave
        descifrado_bin = "".join(['1' if t != k else '0' for t, k in zip(texto_cifrado_bin, clave_bin)])
        
        # Convertir el resultado binario a texto
        return self._from_binary_string(descifrado_bin)


class CifradoCesar:
    def __init__(self, desplazamiento=3):
        self.alfabeto = "ABCDEFGHIJKLMNÑOPQRSTUVWXYZ"
        self.desplazamiento = desplazamiento

    def cifrar(self, texto: str) -> str:
        #print(texto)
        texto_cifrado = ''.join([self._desplazar_caracter(caracter) for caracter in texto.upper()])
        #print(texto_cifrado)
        return texto_cifrado

    def descifrar(self, texto_cifrado: str) -> str:
        texto_descifrado = ''.join([self._desplazar_caracter(caracter, -self.desplazamiento) for caracter in texto_cifrado.upper()])
        return texto_descifrado 

    def _desplazar_caracter(self, caracter: str, valor_desplazamiento=None) -> str:
        if valor_desplazamiento is None:
            valor_desplazamiento = self.desplazamiento
        if caracter in self.alfabeto:
            idx = (self.alfabeto.index(caracter) + valor_desplazamiento) % len(self.alfabeto)
            return self.alfabeto[idx]
        else:
            return caracter

def administrar_chatbot(text,number, messageId, name):
    text = text.lower() #mensaje que envio el usuario
    list = []
    print("mensaje del usuario: ",text)

    markRead = markRead_Message(messageId)
    list.append(markRead)
    time.sleep(2)

    texto_cifrar = ""
    clave_cifrar = ""

    if "hola" in text:
        body = "¡Hola! 👋 Bienvenido al bot cifrador de la UCSM. ¿Cómo podemos ayudarte hoy?"
        footer = "Nicolás y Carlos"
        options = ["🔒 Cifrar", "🔓 Descifrado"]

        replyButtonData = buttonReply_Message(number, options, body, footer, "sed1",messageId)
        replyReaction = replyReaction_Message(number, messageId, "🫡")
        list.append(replyReaction)
        list.append(replyButtonData)

    elif "cifrar" in text:
       
        textMessage = text_Message(number,"Genial, por favor ingresa tu texto a cifrar con nuestro chatbot inteligente 🤖. \n👉 Para ingresar el texto sigue el siguiente formato por favor: 'Texto: <texto>'")

        list.append(textMessage)

    elif "texto:" in text:
       
        textMessage = text_Message(number,"Genial, ingresaste el texto correctamente")
        texto_cifrar = text
        listaValsCypher.append(texto_cifrar)
        time.sleep(3)

        textMessage2 = text_Message(number,"Ahora, por favor ingresa tu clave 🤖. \n👉 Para ingresar la clave sigue el siguiente formato por favor: 'Clave: <clave>'")

        print(texto_cifrar)

        list.append(textMessage)
        list.append(textMessage2)

    elif "clave:" in text:
       
        textMessage = text_Message(number,"Genial, ingresaste la clave correctamente. Espera mientras ciframos tu texto por favor 😬")
        clave_cifrar = text
        listaValsCypher.append(clave_cifrar)
        time.sleep(3)

        textMessage2 = text_Message(number,"Lo tenemos 😁")
        time.sleep(3)

        #cifrado_vernam = vernam.cifrar(texto_cifrar, clave_cifrar)
        #cifrado_cesar = cesar.cifrar(cifrado_vernam)

        textMessage3 = text_Message(number,"Tu texto cifrado es ⬇️")

        mensajeCifrado = text_Message_cifrado(number)
        
        #print("---------------------------------------", listaValsCypher[0], listaValsCypher[1])
        print("---------------------------------------", texto_cifrar, clave_cifrar)

        list.append(textMessage)
        list.append(textMessage2)
        list.append(textMessage3)
        list.append(mensajeCifrado)

    elif "descifrado" in text:
        
        textMessage = text_Message(number,"Genial, por favor ingresa tu texto a descifrar con nuestro chatbot inteligente 🤖. \n👉 Para ingresar el texto sigue el siguiente formato por favor: 'des_text: <texto>'")

        list.append(textMessage)
    
    elif "des_text:" in text:
       
        textMessage = text_Message(number,"Genial, ingresaste el texto a descifrar correctamente")
        texto_descifrar = text
        listaValsUncypher.append(texto_descifrar)
        time.sleep(3)

        textMessage2 = text_Message(number,"Ahora, por favor ingresa tu clave 🤖. \n👉 Para ingresar la clave sigue el siguiente formato por favor: 'des_key: <clave>'")

        print(texto_descifrar)

        list.append(textMessage)
        list.append(textMessage2)

    elif "des_key:" in text:
       
        textMessage = text_Message(number,"Genial, ingresaste la clave correctamente. Espera mientras desciframos tu texto por favor 😬")
        clave_descifrar = text
        listaValsUncypher.append(clave_descifrar)
        time.sleep(3)

        textMessage2 = text_Message(number,"Lo tenemos 😁")
        time.sleep(3)

        #cifrado_vernam = vernam.cifrar(texto_cifrar, clave_cifrar)
        #cifrado_cesar = cesar.cifrar(cifrado_vernam)

        textMessage3 = text_Message(number,"Tu texto descifrado es ⬇️")

        mensajeDescifrado = text_Message_descifrado(number)
        
        #print("---------------------------------------", listaValsCypher[0], listaValsCypher[1])
        print("---------------------------------------", texto_cifrar, clave_cifrar)

        list.append(textMessage)
        list.append(textMessage2)
        list.append(textMessage3)
        list.append(mensajeDescifrado)
      
    else :
        data = text_Message(number,"Lo siento, no entendí lo que dijiste 🥺. Intentalo de nuevo 😎")
        list.append(data)

    for item in list:
        enviar_Mensaje_whatsapp(item)