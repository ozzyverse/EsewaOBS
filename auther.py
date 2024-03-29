import requests
import configparser
from datetime import date 
import os
import base64 
today = date.today() 
Ua= 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:80.0) Gecko/20100101 Firefox/80.0'
config = configparser.ConfigParser()
path = '/'.join((os.path.abspath(__file__).replace('\\', '/')).split('/')[:-1])
config.read(os.path.join(path, 'config.conf'))
email = config['config']['email']
password = config['config']['password']
def get_encoded_pass(string):
    sample_string = string
    sample_string_bytes = sample_string.encode("ascii") 
    
    base64_bytes = base64.b64encode(sample_string_bytes) 
    base64_string = base64_bytes.decode("ascii") 
    return base64_string
password = get_encoded_pass(password)
def get_session():
    url = 'https://esewa.com.np/authenticate?redirectForm='
    headers = {'User-Agent':Ua,
    'Accept':'application/json, text/plain, */*',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate',
    'esewa_id': email,
    'password': password,
    'Content-Type':'application/json;charset=utf-8'}
    r=requests.post(url,headers=headers)
    
    cook = (r.headers['set-cookie'])
    
    authesewa = cook.split(' HttpOnly; Secure, ')[1].split('; Max-Age=86400;')[0].replace('authesewa=','')
    XXSRFTOKENES = cook.split(' Secure, XSRF-TOKEN=')[1].split('; Path=/; Secure,')[0]
    return {'authesewa':authesewa,'X-XSRF-TOKEN-ES':XXSRFTOKENES}


def get_most_recent_transaction():
    url= f'https://esewa.com.np/api/web/auth/transactions?channel=ALL&from_date=2020-09-09&page=0&product_id=1&prop_value=&size=15&status=COMPLETE&to_date={today}&type=CR'
    datas = get_session()
    headers = {'User-Agent':Ua,
    'X-XSRF-TOKEN-ES':datas['X-XSRF-TOKEN-ES']}
    cookies={'authesewa':datas['authesewa']}
    r=requests.get(url,headers=headers,cookies=cookies).json()
    transaction_code = r[0]['transaction_code']
    transaction_ver = r[0]['transaction_version']
    module_id = r[0]['module_id']
    trans_url =f'https://esewa.com.np/api/web/auth/transactions/{transaction_code}?module_id={module_id}&transaction_version={transaction_ver}'
    full_details = requests.get(trans_url,headers=headers,cookies=cookies).json()
    sender_name = full_details['properties']['senderName']
    remarks = full_details['properties']['remarks']
    amount= full_details['amount']
    dict = {'sender':sender_name,'amount':amount,'remarks':remarks}
    return dict

if __name__ == "__main__":
    get_most_recent_transaction()
