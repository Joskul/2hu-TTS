from gtts import gTTS
from bs4 import BeautifulSoup
from bs4.element import Comment
import requests
import re
import urllib
import os
import glob
from youtube_search import YoutubeSearch
from pytube import YouTube
from google_images_search import GoogleImagesSearch
import ffmpeg

gis = GoogleImagesSearch(API, PROJECT_CX)

chap = input("Chapter: ")

URL = 'https://writer.dek-d.com/marisafc/story/viewlongc.php?id=864471&chapter=' + chap
page = requests.get(URL, proxies={'http':'118.174.232.243:8080'}, headers= {'User-Agent' : 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36'})
soup = BeautifulSoup(page.text.encode('UTF-8'), 'html.parser')
results = soup.find(id='story-content')
[s.extract() for s in results(['style', 'script', '[document]', 'head', 'title'])]

text = '\n'.join(results.getText().split('\n')[:-21]).replace('[C]', '').replace('  ','\n').replace('ความอันตราย :', '\nความอันตราย :').replace('สถานที่หลักในการทำกิจกรรม :', '\nสถานที่หลักในการทำกิจกรรม :')\
    .replace('ความเป็นมิตรต่อมนุษย์ :','\nความเป็นมิตรต่อมนุษย์ :').replace('ความสามารถ :','\nความสามารถ :').replace('ที่อยู่อาศัย :','\nที่อยู่อาศัย :').replace('ชื่ออังกฤษ :','\nชื่ออังกฤษ :').replace('ที่อยู่ : ','\nที่อยู่ : ')\
        .replace('* *',' *')
text = re.sub(r'http\S+', '', text)

f = open('content.txt', 'w', encoding='UTF-8')
f.write(text)
f.close()
try:
    name = text.split('{', 1)[1].split('}')[0]
    name = "".join(re.split("[^a-zA-Z]*", name))
    name = re.sub(r"(\w)([A-Z])", r"\1 \2", name)
except: name = ''

if(len(name) <= 1):
    name = text[:100]
    name = "".join(re.split("[^a-zA-Z]*", name))
    name = re.sub(r"(\w)([A-Z])", r"\1 \2", name)
print(name)

sf = './out/tts/tts{} - {}.mp3'.format(chap,name)
bgm = "./out/bgm/BGM-{}.webm".format(chap)
thb = './out/thumbnails/char{}.jpg'.format(chap)
out = './out/Chapter {} - {}.mp4'.format(chap,name)

if not(os.path.isfile(sf)):
    t = text.replace(name,'').replace('{', '').replace('}', '').replace('[', '').replace(']', '').replace(' ', '').replace('.', '').replace('+', '').replace('\n','\n,')
    tts = gTTS(t, lang = 'th')
    tts.save(sf)
    print('TTS ready!')
else: print('TTS already exists')

done = False

if not(os.path.isfile(bgm)):
    while not done:
        try:
            search_results = YoutubeSearch('Touhou ' + name + "'s theme extended -hour", max_results=1).to_dict()
            video = 'https://www.youtube.com/watch?v=' + search_results[0]['id']
            stream = YouTube(video).streams.filter(file_extension='webm',only_audio=True)
            stream[0].download(output_path="./out/bgm", filename="BGM-{}".format(chap))
            print('BGM ready!')
            done = True
        except: 
            print('Error! Retrying') 
            pass
else: print('BGM already exists')


if not(os.path.isfile(thb)):
    gis.search(search_params = {'q': name, 'num': 1}, path_to_dir = './out/thumbnails/')
    latest_file = max(glob.glob('./out/thumbnails/*'), key=os.path.getctime)
    os.rename(latest_file, thb)
    print('Thumbnail ready!')
else: print('Thumbnail already exists')


mu = ffmpeg.input(bgm).filter('volume', 0.05)
vo = ffmpeg.input(sf).filter('volume', 1.125).filter('atempo', 1.725).filter('asetrate', 19500).filter('acompressor',ratio = 5, attack = 100, release = 1000)
im = ffmpeg.input(thb)
au = ffmpeg.filter([vo, mu], 'amix', duration='first')

(
    ffmpeg
    .concat(im, au, v=1, a=1)
    .output(out, vcodec='mjpeg', acodec='aac')
    .run(overwrite_output=True)
)