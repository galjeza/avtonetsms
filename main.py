
class Contact:
    def __init__(self,phoneNumber,car,price,letnik,url,place):
        self.phoneNumber = phoneNumber
        self.car = car
        self.price = price
        self.letnik = letnik
        self.url = url
        self.place = place
def insertContact(contact):
    now = datetime.now()
    dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
    scope = ["https://spreadsheets.google.com/feeds", 'https://www.googleapis.com/auth/spreadsheets',
             "https://www.googleapis.com/auth/drive", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name('avtonetsms-334112-98979d11fd82.json', scope)
    client = gspread.authorize(creds)
    sheet2 = client.open("AvtonetSMS").get_worksheet(1)
    procent = sheet2.cell(4,1).value.strip()
    sheet = client.open("AvtonetSMS").sheet1
    val = worksheet.acell('B22').value
    print("TESTING VAL")
    print(val)
    cell =sheet.find(contact.phoneNumber)
    if(cell is None):
        cena = int(re.sub('\D', '', contact.price))
        ponujena_cena = cena - (cena*(int(procent)/100))
        ponujena_cena = round(ponujena_cena/10)*10
        ponujena_cena = str(ponujena_cena) + " €"
        sheet.append_row([contact.phoneNumber,contact.url,contact.price,contact.car,contact.letnik,contact.place,dt_string,ponujena_cena])
        return True
    return False

def insertInfo(adUrl,driver):
    print("=> Getting contact data from: "+adUrl+".")
    driver.get(adUrl)
    soup = BeautifulSoup(driver.page_source)
    tel = soup.find(class_="h4 font-weight-bold m-0").text.strip().replace(" ", "")
    try:
        price = soup.find(class_="h2 font-weight-bold align-middle py-4 mb-0").text.strip().replace(" ", "")

    except:
        price = soup.find(class_="h4 font-weight-bold text-muted align-middle py-4").text.strip()
    letnik = soup.find(text="Prva registracija:").find_next('td').text.replace(" ", "").partition('/')[0].strip()
    place = soup.find(text="Kraj ogleda:").find_next('td').text.strip()
    place = ''.join([i for i in place if not i.isdigit()])
    car = soup.find("h3").text.strip()
    contact = Contact(tel, car, price, letnik, adUrl, place)
    print("=> Recieved data")
    if(insertContact(contact)):
        return contact
    else:
        return False


def find_between(s, start, end):
    return (s.split(start))[1].split(end)[0]

    
    
def stripTheAds(ads):
    refactored_ads = []
    scope = ["https://spreadsheets.google.com/feeds", 'https://www.googleapis.com/auth/spreadsheets',
             "https://www.googleapis.com/auth/drive", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name('avtonetsms-334112-98979d11fd82.json', scope)
    client = gspread.authorize(creds)
    sheet = client.open("AvtonetSMS").sheet1

    for ad in ads :
        time.sleep(0.7)
        if(sheet.find(ad)==None):
            refactored_ads.append(ad)



    return refactored_ads


def getUrls(urls):
    ads = []
    driver = setup_webdriver()
    for url in urls:
        print("=> Getting ads from:" + url + ".")
        driver.get(url)
        time.sleep(8)
        site = WebDriverWait(driver, 100000).until(EC.presence_of_element_located((By.NAME, 'Avto.net')))
        
        soup = BeautifulSoup(driver.page_source, "html.parser")
        print("=> Recieved page source.")
        print("=> Getting ad URLs from page source.")
        results = soup.find_all("div", class_="row bg-white position-relative GO-Results-Row GO-Shadow-B")
        print("=> Found " + str(len(results)) + " URls.")
        for result in results:
            if (len(result.find_all("div", {"class": "GO-Results-Top-BadgeTop"})) < 1):
                link = result.find("a", class_="stretched-link")
                link = link['href']
                idOglasa = find_between(link, "id=", "&")
                result_url = "https://www.avto.net/Ads/details.asp?id=" + idOglasa
                ads.append(result_url)
            else:
                print("Najden avto v top ponudbi")

    driver.quit()

    ads = stripTheAds(ads)
    print("=> Found "+ str(len(ads))+ " new ads.")

    return ads

def setup_webdriver():
    print("=> Setting up webdriver.")
    chrome_options = Options()
    chrome_options.add_argument('--ignore-certificate-errors')
    chrome_options.add_argument('--ignore-ssl-errors')                      
    driver = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options)
    print("=> vsi gonilniki uspešno pridobljeni")
    driver.get("https://www.avto.net/_2016mojavtonet/")
    driver.maximize_window()

    return driver


def sendSMS(oglasi,sporocilo,procent):
    driver = setup_webdriver()
    driver.get("https://www.smsapi.si/prijava")
    emailInput = driver.find_element_by_id("c_users_email")
    emailInput.click()
    emailInput.send_keys("vitalteam.dj@gmail.com")
    passInput = driver.find_element_by_id("c_users_password")
    passInput.click()
    passInput.send_keys("vital1985")
    driver.find_element_by_id("submitButton").click()
    site = WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.ID, 'topNavigation')))






    for oglas in oglasi:
        cena = int(re.sub('\D', '', oglas.get("cena")))
        if(cena != 0):
            ponujena_cena = cena - (cena*(int(procent)/100))
            print("Cena:"+ str(cena))
        
            ponujena_cena = int(math.floor(ponujena_cena/100.0))*100
            ponujena_cena = str(ponujena_cena) + " €"
            print("ponujena cen:"+str(ponujena_cena))
            driver.get("https://www.smsapi.si/prejemniki/poslji-sms")
            idbtn =  WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.ID, 'c_users_country_code')))
            driver.find_element_by_id("c_users_tel_numbers").click()
            driver.find_element_by_id("c_users_tel_numbers").send_keys(oglas.get("stevilka"))
            driver.find_element_by_id("c_users_msg").click()
            driver.find_element_by_id("c_users_msg").send_keys(sporocilo.replace("$CENA",ponujena_cena))
            driver.find_element_by_id("submitButton").click()
            time.sleep(5)
        print("=> Pošiljam sms na tel številko: "+oglas.get("stevilka"))
        
        
        
        
    return True

def printMoney(url,sporocilo,procent):
    for i in range(99):
        try:

            urls = getUrls(url)
            break
        except Exception as e:
           print(e)


    driver = setup_webdriver()
    oglasi = []
    for adUrl in urls:

        time.sleep(2)
        for i in range(10):

            try:
                contact = insertInfo(adUrl,driver)
                if(contact != False):
                    oglasi.append({
                        "cena":contact.price,
                        "stevilka":contact.phoneNumber
                    })
                break
            except Exception as e:
                print(traceback.format_exc())
                driver.quit()
                driver = setup_webdriver()
    driver.quit()
    print(oglasi)
    sendSMS(oglasi,sporocilo,procent)

def getParameters():
    scope = ["https://spreadsheets.google.com/feeds", 'https://www.googleapis.com/auth/spreadsheets',
             "https://www.googleapis.com/auth/drive", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name('avtonetsms-334112-98979d11fd82.json', scope)
    client = gspread.authorize(creds)
    sheet = client.open("AvtonetSMS").get_worksheet(1)
    x = [item for item in sheet.col_values(2) if item]
    x.pop(0)
    urls = []
    for link in x:
        url = link.strip()
        urls.append(url)


    sporocilo = sheet.cell(2,1).value.strip()


    data = {
        "urls": urls,
        "sporocilo": sporocilo,
        "procent": sheet.cell(4,1).value.strip()
    }
    return data




try:
    parameters = getParameters()
    urls =  parameters.get("urls")
    sporocilo = parameters.get("sporocilo")
    procent = parameters.get("procent")
    # setupProxy()
    printMoney(urls,sporocilo,procent)
except Exception as e:
    print(e)
    time.sleep(10)
    print(e)
    

print("=> Proces uspešno zaključen.")
