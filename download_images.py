import urllib.request
headers = {'User-Agent': 'BioethicsCourseBot/1.0 (https://github.com/brendanpshea/bioethics)'}

images = [
    ('hippocrates.jpg', 'https://upload.wikimedia.org/wikipedia/commons/1/14/Hippocrates_Rubens.jpg'),
    ('nuremberg_trial.jpg', 'https://upload.wikimedia.org/wikipedia/commons/c/cf/Nuremberg_Doctors%27_Trial.jpg'),
    ('tuskegee.jpg', 'https://upload.wikimedia.org/wikipedia/commons/4/4b/Tuskegee-syphilis-study_doctor-drawing-blood.jpg')
]

for name, url in images:
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req) as response, open(f'/workspaces/bioethics/images/{name}', 'wb') as out_file:
            data = response.read()
            out_file.write(data)
            print(f"Downloaded {name}")
    except Exception as e:
        print(f"Error downloading {name}: {e}")
