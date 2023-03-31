import CreatePdf
from PIL import Image, ImageFont
import datetime
import boto3
from io import BytesIO
import os
import json

iPath = os.environ.get('iPath')
oPath = os.environ.get('oPath')
BUCKET_NAME = os.environ.get('BUCKET_NAME')
config = {}

# event:
#{
#    base: string,
#    items:[{
#       prefix: string,
#       suffix: string,
#       letter: string
#    },...
#   ],
#    solicitor: {
#       cpf: string
#    },
#    info: {
#       date: Date
#   }
#}
s3Client = boto3.client('s3')

def handler(event, context):
    jEvent = json.loads(event['body'])
    set_arguments(jEvent)
    configuring(jEvent)
    for item in jEvent["items"]:
        list_files(iPath + '/' + make_suffix(item['suffix'], item.get('letter', None)), '{p}_{s}{l}'.format(p=item['prefix'], s=item['suffix'], l=item.get('letter','')))

def configuring(cfg):
    #defining config
    global config
    config = CreatePdf.Config(
            get_watermark_image(), 
            get_font(), 
            make_footer_text(cfg['solicitor']['cpf']), 
            100, 100, #marginX, marginY
            (255,0,0)
            )

def set_arguments(arguments):
    global iPath
    iPath = iPath + arguments["base"]
    global oPath
    oPath = oPath + arguments["base"]

def make_suffix(suffix, letter):
    sfx = '2_'+'%07d'%suffix
    if letter is not None:
        sfx = sfx + letter
    return sfx

def list_files(prefix, fileName):
    files = s3Client.list_objects_v2(Bucket= BUCKET_NAME , Prefix=prefix)
    if files.get('Contents', None) is not None:
        imgs = []
        for item in files['Contents']:
            imgs.append(load_images_v2(item))
        result = CreatePdf.create_pdf(imgs, config)
        #with open('output.pdf', 'wb') as f:
        #   f.write(result.getbuffer())
        save_on_s3(result, '{o}/{n}'.format(o=oPath, n=fileName))

def load_images_v2(path):
    obj = s3Client.get_object(Bucket=BUCKET_NAME, Key=path['Key'])['Body']
    img = Image.open(BytesIO(obj.read()))
    obj.close()
    return img

def save_on_s3(file, prefix):
    # the file pointer is at the end of the file. Seeking the pointer back to start
    file.seek(0)
    s3Client.put_object(Bucket=BUCKET_NAME, Key=prefix, Body=file, ServerSideEncryption='AES256')

def get_watermark_image():
    global watermarkImage
    return Image.open('resources/watermark.png')

def get_font():
        return ImageFont.truetype('resources/Helvetica-Bold-Font.ttf', 36)

def make_footer_text(cpf):
    cpf_text = ''
    if cpf != '':
        cpf_text = 'Solicitado por: %s - ' % cpf
    return cpf_text + 'Data da Solicitação: ' + get_generation_date()

def get_generation_date(date=None):
    if date is None:
        date = datetime.datetime.now() 
    return '%s/%s/%s %s' % (date.day, date.month, date.year, date.strftime('%X'))

