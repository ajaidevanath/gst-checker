from flask import Flask, request, jsonify,render_template
from pdf2image import convert_from_path
from paddleocr import PaddleOCR
from werkzeug.utils import secure_filename
import requests 
import pandas as pd 
import re
from IPython.display import HTML 
app = Flask(__name__)
#from app import app as application 
#from app import create_app 
#application = create_app()
#app.config['UPLOAD_FOLDER'] = 'static/files'
ocr = PaddleOCR(use_angle_cls=True, lang='en')

@app.route('/', methods=['GET', 'POST'])
def main():
    return render_template('index.html')

@app.route('/result', methods=['POST'])
def extract_gst():
    if request.method == 'POST':
      f = request.files['imagefile']
      f.save(secure_filename('invoice.pdf'))
    images = convert_from_path('invoice.pdf')
    for i in range(len(images)):
        images[i].save('page-test.jpeg')  
    result = ocr.ocr('page-test.jpeg', cls=True)
    text_blocks = ' '.join([line[1][0] for line in result])
    gst_pattern = r'\d{2}[A-Z]{5}\d{4}[A-Z]{1}\d{1}[Z]{1}[A-Z\d]{1}'
    gst_match = re.search(gst_pattern, text_blocks)
    if gst_match:
        vendor_gst = gst_match.group()
    url = "https://gst-return-status.p.rapidapi.com/free/gstin/"+vendor_gst

    headers = {"Content-Type": "application/json",
	               "X-RapidAPI-Key": "3db1de00femshe13d7a59c604d4ap1fa9f8jsn818c5d02afa3",
	                "X-RapidAPI-Host": "gst-return-status.p.rapidapi.com"
                   }
    response = requests.get(url, headers=headers)
    response = response.json()['data']
    df =pd.DataFrame()
    adding = {'Name of the Company':response['lgnm'],'PAN':response['pan'],'GST':response['gstin'],'e-invoice':response['einvoiceStatus'],'Address':response['adr'],'Pincode':response['pincode']}
    df = pd.DataFrame(adding,index=[0])
    df = df.to_html(classes='table table-stripped')
    return render_template('result.html',var=HTML(df))

if __name__ == '__main__':   
    app.run(debug=False)
