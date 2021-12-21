import requests

def upload_image(image_b64, IMG_API_KEY):
    params = {
        'key':IMG_API_KEY,
        'image': image_b64,

    }
    response = requests.post(url='https://api.imgbb.com/1/upload', data=params)
    print(response.json())
    if response.status_code == 200:
        data = response.json()
        list_data = data['data']
        print(list_data['url'])
        return list_data['url']
    else:
        return response.status_code

IMG_API_KEY = '7a21884aec75ec7ad1a877cfab39e0dd'
upload_image('https://assets.americanliterature.com/al/images/story/little-red-riding-hood.jpg', IMG_API_KEY)
