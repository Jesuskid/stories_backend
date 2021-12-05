import requests

def upload_image(image_b64, IMG_API_KEY):
    params = {
        'key':IMG_API_KEY,
        'image': image_b64,

    }
    response = requests.post(url='https://api.imgbb.com/1/upload', data=params)
    data = response.json()
    list_data = data['data']
    print(list_data['url'])
    return list_data['url']
