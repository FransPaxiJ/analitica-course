import os
from urllib.parse import urlparse
import requests
from PIL import Image
from io import BytesIO
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver import ActionChains
from selenium.webdriver.support.ui import Select
import time

# Crear directorio para descargas si no existe
# download_dir = os.path.join(os.getcwd(), "./hidrometeorologico")
# if not os.path.exists(download_dir):
    # os.makedirs(download_dir)

opts = Options()
opts.add_argument("start-maximized")
opts.add_argument("disable-infobars")
opts.add_argument("--disable-extensions")
opts.add_argument("--disable-blink-features=AutomationControlled")
# opts.add_argument("--headless=new")
# opts.add_argument("--disable-gpu")

chrome_prefs = {
    # No mostrar diálogo de descarga
    "download.prompt_for_download": False,
    # Carpeta por defecto para descargar
    # "download.default_directory": download_dir,
    # Permitir múltiples descargas sin preguntar
    "profile.default_content_settings.popups": 0,
    "profile.default_content_setting_values.automatic_downloads": 1,
    # (opcional) deshabilitar notificaciones del sitio
    "profile.default_content_setting_values.notifications": 2
}

opts.add_experimental_option("prefs", chrome_prefs)

driver_path = "./chromedriver.exe"  # Cambia esto a la ruta de tu chromedriver

driver = webdriver.Chrome(service=Service(driver_path), options=opts)

driver.get('https://www.senamhi.gob.pe/?p=estaciones')

# Esperar a que la página principal cargue
time.sleep(5)

# Primero cambiamos al iframe del mapa

# Esperamos a que el iframe esté presente con una URL más específica
iframe = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.XPATH, "//iframe[contains(@src, 'mapa-estaciones-2')]"))
)

# Cambiamos al contexto del iframe
driver.switch_to.frame(iframe)
print("Cambiado al iframe del mapa")
    
# Esperar un poco para que el contenido del iframe cargue completamente
time.sleep(3)

    # Intentar encontrar el botón de búsqueda usando diferentes selectores
try:
    # Intento 1: XPath genérico para el botón de búsqueda de Leaflet
    search_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//a[contains(@class, 'search-button')]"))
    )
    driver.execute_script("arguments[0].click();", search_button)
    print("Botón de búsqueda clickeado exitosamente")

    # Código para el campo de búsqueda si el botón se clickeó exitosamente
    search_input = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "//input[contains(@class, 'search-input')]"))
    )
    search_input.clear()
    search_input.send_keys("Lima")
    time.sleep(5)  # Espera un poco para que el texto se ingrese
    print("Texto ingresado en el campo de búsqueda")

    # Esperar a que aparezcan las sugerencias y hacer clic en la primera
    first_suggestion = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "//li[@class='search-tip'][1]"))
    )
    first_suggestion.click()
    print("Clic realizado en la primera sugerencia")

    # Esperar a que se genere el nuevo iframe con la URL específica
    try:
        # Esperamos a que aparezca el nuevo iframe que contiene "map_red_graf.php"
        time.sleep(3)  # Dar tiempo para que se cargue el nuevo iframe
        new_iframe2 = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.XPATH, "//iframe[contains(@class, 'iframeLoad')]"))
        )
        print(f"Nuevo iframe encontrado: {new_iframe2.get_attribute('src')}")
        
        # Cambiar al contexto del nuevo iframe
        driver.switch_to.frame(new_iframe2)
        print("Cambiado al contexto del nuevo iframe")
        
        # Ahora buscamos el elemento con clase 'tabl' dentro de este iframe
        time.sleep(2)  # Esperar a que se cargue el contenido del iframe
        
        # Intentamos encontrar el elemento con clase 'tabl' y hacer clic en él
        tabl_element = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//a[contains(@id, 'tabl')]"))
        )
        tabl_element.click()
        time.sleep(5)  # Espera un poco para que el clic se registre
        print("Clic realizado en el elemento con clase 'tabl'")

        # Completamos el captcha
        # Encontramos el span con estilo rojo y texto grande que contiene el código
        captcha_span = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//span[contains(@style, 'color: red; font-size:xxx-large')]"))
        )

        # Extraemos el texto del span (el código del captcha)
        captcha_code = captcha_span.text
        print(f"Código captcha extraído: {captcha_code}")

        # Encontramos el campo de entrada del captcha
        captcha_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "captchaInput"))
        )

        # Ingresamos el código en el campo
        captcha_input.clear()
        captcha_input.send_keys(captcha_code)
        print("Código captcha ingresado correctamente")

        # hacemos click en el botón de enviar
        submit_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(@id, 'entrar')]"))
        )
        driver.execute_script("arguments[0].click();", submit_button)
        time.sleep(5)  # Espera un poco para que el clic se registre
        print("Botón de enviar clickeado correctamente")
        time.sleep(5)

        # Localizamos el elemento select
        select_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//select[contains(@id, 'CBOFiltro')]"))
        )

        # Creamos un objeto Select y seleccionamos una opción
        select = Select(select_element)
        time.sleep(2)  # Breve pausa para estabilidad

        # Obtenemos el número de opciones disponibles
        options = select.options
        print(f"Total de opciones disponibles: {len(options)}")

        # Iteramos por cada opción del select
        for index in range(len(options)):
            try: 

                print(f"\nSeleccionando opción {index}: {options[index].text}")
                
                # Localizamos el select nuevamente (por si el DOM se actualizó)
                select_element = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, "//select[contains(@id, 'CBOFiltro')]"))
                )
                select = Select(select_element)
                
                # Seleccionamos la opción actual
                select.select_by_index(index)
                time.sleep(5)  # Esperamos a que la página se actualice
                print(f"Opción {index} seleccionada correctamente")

                # cambiamos de iframe donde esta el CSV
                time.sleep(3) 
                new_iframe3 = WebDriverWait(driver, 15).until(
                    EC.presence_of_element_located((By.XPATH, "//iframe[contains(@id, 'contenedor')]"))
                )
                
                # Cambiar al contexto del nuevo iframe
                driver.switch_to.frame(new_iframe3)
                print("Cambiado al contexto del nuevo iframe")

                # Hacemos click en el botón de Exportar a CSV
                export_button = WebDriverWait(driver, 15).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(@id, 'export2')]"))
                )
                driver.execute_script("arguments[0].click();", export_button)
                time.sleep(5)  # Esperamos a que se complete la descarga
                print(f"Click en el boton de Exportar CSV realizado con exito")

                # Volvemos al frame principal después de cada descarga
                driver.switch_to.default_content()
                
                # Volvemos al primer iframe (iframe del mapa)
                iframe = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, "//iframe[contains(@src, 'mapa-estaciones-2')]"))
                )
                driver.switch_to.frame(iframe)
                
                # Volvemos al segundo iframe
                new_iframe2 = WebDriverWait(driver, 15).until(
                    EC.presence_of_element_located((By.XPATH, "//iframe[contains(@class, 'iframeLoad')]"))
                )
                driver.switch_to.frame(new_iframe2)
                print("Volvimos al iframe principal para continuar con la siguiente opción")

            except Exception as e:
                print(f"Error al seleccionar la opción {index}: {e}")
                # Intentamos volver al contexto correcto en caso de error
                try:
                    driver.switch_to.default_content()
                    iframe = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.XPATH, "//iframe[contains(@src, 'mapa-estaciones-2')]"))
                    )
                    driver.switch_to.frame(iframe)
                    new_iframe2 = WebDriverWait(driver, 15).until(
                        EC.presence_of_element_located((By.XPATH, "//iframe[contains(@class, 'iframeLoad')]"))
                    )
                    driver.switch_to.frame(new_iframe2)
                    print("Recuperado el contexto después de un error")
                except Exception as iframe_error:
                    print(f"No se pudo recuperar el contexto: {iframe_error}")
                continue      
        
    except Exception as e:
        print(f"Error al interactuar con el nuevo iframe 2: {e}")
        exit(1)

except Exception as e:
    print(f"Error al interactuar con el iframe 1: {e}")
    exit(1)

