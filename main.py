import os
import json
import uuid
import matplotlib.pyplot as plt
from PIL import Image
from scipy.spatial import distance
from box import BoundingBox
from detection import inference
from keypoint import keypoint
from xmi import diagram_to_xmi
from ocr import ocr

debug = True


def crop_image(box, image):
    lt_coords = box.coordinates[0]
    br_coords = box.coordinates[3]

    return image.crop((lt_coords[0], lt_coords[1], br_coords[0], br_coords[1]))


def get_closest_box_to_point(point, boxes):
    closest_b = None
    min_distance = float('inf')

    for b in boxes:
        euc_distance = distance.euclidean(point, b.coordinates[4])
        if euc_distance < min_distance:
            min_distance = euc_distance
            closest_b = b

    return closest_b


# Read image
script_dir = os.path.dirname(__file__)  # <-- absolute dir the script is in
rel_path = "detection\data\images\PA24.png"
abs_file_path = os.path.join(script_dir, rel_path)
image = Image.open(abs_file_path)
image = image.convert("RGB")

# Do inference
print('Running inference for {}... '.format(abs_file_path), end='')
img_for_plot, detections, category_index = inference.inference(image, min_thresh=.5)

# Plot inference
inference.plot_inference(img_for_plot, detections)

# Map to box items
boxes = []
for i in range(len(detections['detection_scores'])):
    box = BoundingBox(
        image,
        detections['detection_boxes'][i],
        category_index[detections['detection_classes'][i]]['name'],
        detections['detection_scores'][i]
    )
    boxes.append(box)

# Digitize text for 'text' boxes
for b in boxes:
    if b.label == 'text':
        img_res = crop_image(b, image)
        b.text = ocr.image_to_string(img_res)

        if "extension points\n" in b.text:
            b.used = True

# Attach text to elements

# ---> Set name to use_case elements
use_case_boxes = list(filter(lambda x: x.label == 'use_case', boxes))

for uc_b in use_case_boxes:
    t_b = get_closest_box_to_point(
        uc_b.coordinates[4],
        list(filter(lambda x: x.label == 'text' and not x.used and not "extension points" in x.text, boxes))
    )

    t_b.used = True
    uc_b.text = t_b.text

# ---> Set dotted_line type and extension + actor names
text_boxes = list(filter(lambda x: x.label == 'text' and x.used == False, boxes))
non_text_boxes = list(filter(lambda x: (x.label == 'dotted_line' or x.label == 'actor') and x.text is None, boxes))

for t_b in text_boxes:
    nt_b = get_closest_box_to_point(t_b.coordinates[4], non_text_boxes)

    t_b.used = True
    if nt_b.text is None:
        nt_b.text = t_b.text
    else:
        nt_b.text = nt_b.text + "<--->" + t_b.text

# Calculate key points
associations = list(
    filter(lambda x: x.label == 'generalization' or x.label == 'dotted_line' or x.label == 'line', boxes))

for assoc in associations:
    assoc_image = crop_image(assoc, image)
    assoc.key_points = keypoint.calculate_key_points(assoc_image, assoc)


# Connect association with elements
def gen_json(el):
    return {
        'id': el.id,
        'type': 'association' if el.label == 'line' else el.label,
        'name': el.text
    }


def get_or_create_element(diagram, el):
    items = list(filter(lambda x: x['id'] == el.id, diagram['elements']))
    return items[0] if len(items) > 0 else gen_json(el)


diagram = {
    "name": "Generated UC Diagram",
    "elements": []
}

associations = list(
    filter(lambda x: x.label == 'generalization' or x.label == 'dotted_line' or x.label == 'line', boxes))
target_elements = list(
    filter(lambda x: x.label == 'use_case' or x.label == 'actor', boxes))

for assoc in associations:
    start_kp_el = get_closest_box_to_point(assoc.key_points.start, target_elements)
    end_kp_el = get_closest_box_to_point(assoc.key_points.end, target_elements)

    start_kp_el_json = get_or_create_element(diagram, start_kp_el)
    end_kp_el_json = get_or_create_element(diagram, end_kp_el)

    if assoc.label == 'dotted_line' and "include" in assoc.text:
        start_kp_el_json['include'] = {
            'type': 'include',
            'ref': end_kp_el.id
        }
    elif assoc.label == 'dotted_line' and "extend" in assoc.text:
        extensions = list(filter(lambda x: "extend" not in x, assoc.text.split("<-->")))
        extension = extensions[0] if len(extensions) >= 1 else "Default_extension"

        extend_id = uuid.uuid4().hex
        extension_id = uuid.uuid4().hex
        start_kp_el_json['extend_from'] = {
            "type": 'extension_point',
            "extend_id": extend_id,
            "extension_id": extension_id,
            "name": extension
        }

        end_kp_el_json['extend_to'] = {
            "type": "extend",
            "ref": start_kp_el.id,
            "extend_id": extend_id,
            "extension_id": extension_id
        }

    elif assoc.label == 'generalization':
        end_kp_el_json['generalization'] = {
            "type": "generalization",
            "ref": start_kp_el.id
        }
    else:
        assoc_el_json = gen_json(assoc)
        assoc_el_json['start'] = start_kp_el.id
        assoc_el_json['end'] = end_kp_el.id
        diagram['elements'].append(assoc_el_json)

    existing_ids = list(map(lambda x: x['id'], diagram['elements']))
    if start_kp_el.id not in existing_ids:
        diagram['elements'].append(start_kp_el_json)

    if end_kp_el.id not in existing_ids:
        diagram['elements'].append(end_kp_el_json)

    diagram['elements'] = [el if el['id'] is not start_kp_el.id else start_kp_el_json for el in diagram['elements']]
    diagram['elements'] = [el if el['id'] is not end_kp_el.id else end_kp_el_json for el in diagram['elements']]

diagram_json = json.dumps(diagram)
print("Diagram json", diagram_json)

# Convert to XMI
xmi = diagram_to_xmi.convert_to_xmi(diagram)

if debug:
    print("Xmi", xmi)
    plt.show()
