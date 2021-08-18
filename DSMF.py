# -*- coding: utf-8 -*-
from ctypes import *
import requests
import time
import sys
import os
import re

URL = 'https://discord.com/api/v9/users/@me/settings'

class OPENFILENAMEA(Structure):
    _fields_ = [
        ('lStructSize', c_ulong),
        ('hwndOwner', c_void_p),
        ('hInstance', c_void_p),
        ('lpstrFilter', c_char_p),
        ('lpstrCustomFilter', c_char_p),
        ('nMaxCustFilter', c_ulong),
        ('nFilterIndex', c_ulong),
        ('lpstrFile', c_char_p),
        ('nMaxFile', c_ulong),
        ('lpstrFileTitle', c_char_p),
        ('nMaxFileTitle', c_ulong),
        ('lpstrInitialDir', c_char_p),
        ('lpstrTitle', c_char_p),
        ('Flags', c_ulong),
        ('nFileOffset', c_ushort),
        ('nFileExtension', c_ushort),
        ('lpstrDefExt', c_char_p),
        ('lCustData', c_ulonglong),
        ('lpfnHook', c_void_p),
        ('lpTemplateName', c_char_p),
        ('pvReserved', c_void_p),
        ('dwReserved', c_ulong),
        ('FlagsEx', c_ulong)
    ]

def change_message(token, message):
    headers = { 'Host' : 'discord.com', 'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36', 'Content-Type' : 'application/json', 'Authorization' : token, 'Accept' : '*/*', 'Origin' : 'https://discord.com', 'Accept-Encoding' : 'gzip, deflate' }
    
    if message == None:
        payload = {'custom_status':None}
    else:
        payload = {'custom_status':{'text':message}}

    response = requests.patch(URL, json=payload, headers=headers)

    if response.status_code == 200:
        return True
    else:
        return False

def token_check(token):
    return change_message(token, None)

def find_token():
    path = os.getenv('APPDATA') + '\\Discord'

    tokens = []

    if not os.path.exists(path):
        print('[-] Discord not found!')
        sys.exit(-1)

    path += '\\Local Storage\\leveldb'

    for file_name in os.listdir(path):
        if not file_name.endswith('.log') and not file_name.endswith('.ldb'):
            continue

        for line in [x.strip() for x in open(f'{path}\\{file_name}', errors='ignore').readlines() if x.strip()]:
            for regex in (r'[\w-]{24}\.[\w-]{6}\.[\w-]{27}', r'mfa\.[\w-]{84}'):
                for token in re.findall(regex, line):
                    tokens.append(token)

    return tokens

def select_file():
    OpenFileName = OPENFILENAMEA()

    memset(byref(OpenFileName), 0x00, sizeof(OpenFileName))

    lpstrFile = (c_char * 256)()

    OpenFileName.lStructSize = sizeof(OPENFILENAMEA)
    OpenFileName.lpstrFilter = c_char_p(b'Every File(*.*)\0*.*\0\0')
    OpenFileName.lpstrFile = addressof(lpstrFile)
    OpenFileName.nMaxFile = 256

    comdlg32 = windll.LoadLibrary('Comdlg32.dll')
    comdlg32.GetOpenFileNameA(byref(OpenFileName))

    return lpstrFile.value.decode()

tokens = find_token()
token = None

for t in tokens:
    if token_check(t):
        token = t
        break

if len(sys.argv) == 2:
    filename = sys.argv[1]
else:
    filename = select_file()

if token == None:
    print('[-] Discord token not found!')
    sys.exit(-1)
else:
    print("[+] Discord token found!")

if os.path.isfile(filename):
    print("[+] File found!")
    f = open(filename, 'r', encoding='utf-8')
    lyrics = f.read()
    f.close()
else:
    print("[-] File not found!")
    sys.exit(-1)

lyrics = lyrics.replace('\n', ' ')

print('[+] Starting...')

i = 0
try:
    while i < len(lyrics):
        while True:
            if lyrics[i] != ' ':
                break
            i += 1

        message = lyrics[i:i+20]

        if not change_message(token, message):
            break

        print(message)

        i += 1
        time.sleep(2)
except:
    pass

change_message(token, None)