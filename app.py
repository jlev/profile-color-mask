import os
from flask import Flask, request, render_template, g, redirect, Response, url_for, session, send_from_directory
from flask.json import JSONEncoder
from flask import jsonify

import image
from image import convert, detect, mask

templates = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=templates)

# weird trick to get flask to handle numpy int types
class NumpyJSONEncoder(JSONEncoder):
  def default(self, obj):
    try:
      return convert.cv_to_json(obj)
    except TypeError:
      return JSONEncoder.default(self, obj)
app.json_encoder = NumpyJSONEncoder

@app.route('/')
def home():
    return render_template("index.html")

@app.route('/image/detectface', methods=['POST'])
def detect_face():
  # takes a form with a posted image
  # returns face bounding box in canvas coords
  data = request.form.to_dict()
  image = convert.data_uri_to_cv(data.get('image'))
  rect = detect.face(image)
  return jsonify({'rect': convert.cv_rect_to_canvas(rect)})

@app.route('/image/mask', methods=['POST'])
def image_mask():
  data = request.form.to_dict()
  image = convert.data_uri_to_cv(data.get('image'))
  rect = convert.canvas_rect_to_cv(data.get('rect'))
  masked = mask.rect(image, rect)
  return jsonify({'image': convert.cv_to_data_uri(masked)})

# @app.route('/image/refine', methods=['POST'])
# def image_refine():
#   data = request.get_json()
#   new_file = mask.refine(data['image'], data['rect_coords'], data['drawing'])
#   return jsonify()

if __name__ == "__main__":
    app.run(debug=True)