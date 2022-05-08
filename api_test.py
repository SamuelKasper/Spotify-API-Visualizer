
import bmesh
import requests
import os
import cv2
import numpy as np
import webbrowser
import bpy

CLIENT_ID = "56651af3c4134034b9977c0a650b2cdf"
CLIENT_SECRET = "ba05f9e81dbc4443857aa9f3afcfc88b"
REDIRECT_URL = "http://127.0.0.1:5555/callback.html"
# DO NOT PUSH WHEN USER_CODE IS NOT ""!!!
USER_CODE = ""

AUTH_URL = "https://accounts.spotify.com/api/token"
CLIENT_AUTH_URL = "https://accounts.spotify.com/authorize"
BASE_URL = "https://api.spotify.com/v1/"


PLANE_AMOUNT = 100
# get access token
auth_response = requests.post(AUTH_URL, {
    'grant_type': 'client_credentials',
    'client_id': CLIENT_ID,
    'client_secret': CLIENT_SECRET,
})
auth_response_data = auth_response.json()
access_token = auth_response_data['access_token']

headers = {
    'Authorization': 'Bearer {token}'.format(token=access_token)
}

# Opens login screen -> After redirect, you can see the users code. (Live Server must be active!)


def requestAuthorization():
    url = CLIENT_AUTH_URL
    url += "?client_id=" + CLIENT_ID
    url += "&response_type=code"
    url += "&redirect_uri=" + REDIRECT_URL
    url += "&show_dialog=true"
    url += "&scope=user-read-private user-read-email user-modify-playback-state user-read-playback-position user-library-read streaming user-read-playback-state user-read-recently-played playlist-read-private"
    webbrowser.open(url, new=0, autoraise=True)

# Gets song from track id


def getSong(track_id):
    r = requests.get(BASE_URL + "tracks/" + track_id, headers=headers)
    d = r.json()

    artist = d["artists"][0]["name"]
    track = d["name"]
    print("--- Chosen Track ---")
    print(artist, "-", track)
    print()

# Gets cover from song


def getSongImage(track_id):
    getSong(track_id)
    r = requests.get(BASE_URL + "tracks/" + track_id, headers=headers)
    d = r.json()

    # Get image part
    cover_image = requests.get(d["album"]["images"][0]['url'])

    # with open("coverImage.png", 'wb') as f:
    #    f.write(cover_image.content)

    img_string = np.frombuffer(cover_image.content, np.uint8)
    img = cv2.imdecode(img_string, cv2.IMREAD_COLOR)

    createCoverFromImage(img)

    #Get Pixalized
    #img = cv2.imread('coverImage.png')
    resized = cv2.resize(img, (50, 50), interpolation=cv2.INTER_NEAREST)
    cv2.namedWindow('img', cv2.WINDOW_NORMAL)
    cv2.resizeWindow('img', 500, 500)
    cv2.imshow('img', resized)
    cv2.waitKey(0)

# Get image part end

# Gets all albums from artist


def getArtistsAlbums(artist_id):

    r = requests.get(BASE_URL + "artists/" + artist_id,
                     headers=headers)
    a = r.json()

    print("--- All Albums by the Artist '" + a["name"] + "' ---")

    r = requests.get(BASE_URL + "artists/" + artist_id + "/albums",
                     headers=headers,
                     params={"include_groups": "album", "limit": 50})
    d = r.json()

    albums = []
    for album in d["items"]:
        album_name = album["name"]

        trim_name = album_name.split('(')[0].strip()  # Filter out duplicates
        if trim_name.upper() in albums:
            continue

        albums.append(trim_name.upper())

        print(album_name, "---", album["release_date"])

    print()


def createCoverFromImage(img):
    global PLANE_AMOUNT
    bpy.ops.object.select_all(action='SELECT')  # selektiert alle Objekte
    # löscht selektierte objekte
    bpy.ops.object.delete(use_global=False, confirm=False)
    bpy.ops.outliner.orphans_purge()  # löscht überbleibende Meshdaten etc.
    for material in bpy.data.materials:
        bpy.data.materials.remove(material, do_unlink=True) # löschet alle Materialien
    verts = []
    faces = []
    facecolor = []

    cover_mesh = bpy.data.meshes.new("cover mesh")
    cover_object = bpy.data.objects.new("cover", cover_mesh)
    bpy.context.collection.objects.link(cover_object)
    bm = bmesh.new()
    bm.from_mesh(cover_mesh)
    #  erstellt die Verts 
    for x in range(PLANE_AMOUNT + 1):
        verts.append([])
        for y in range(PLANE_AMOUNT + 1):
            new_vert = bm.verts.new(
                (0, int(y - PLANE_AMOUNT/2), -int(x-PLANE_AMOUNT/2)))
            verts[x].append(new_vert)
    # erstellt die faces
    bm.verts.ensure_lookup_table()
    for x in range(len(verts)-1):
        for y in range(len(verts[x])-1):
            new_face = bm.faces.new(
                (verts[x][y], verts[x][y+1], verts[x+1][y+1], verts[x+1][y]))
            faces.append(new_face)
    # erstellst die Matherialien
    rows, cols, _ = img.shape
    for i in range(PLANE_AMOUNT):
        for j in range(PLANE_AMOUNT):
            newMat = bpy.data.materials.new(
                'mat_' + str(i) + "_" + str(j))
            color = img[int(i*rows/PLANE_AMOUNT), int(j*cols/PLANE_AMOUNT)]
            newMat.diffuse_color = ((color[2]/255, color[1]/255, color[0]/255, 1))
            facecolor.append(newMat)
            cover_object.data.materials.append(newMat)
            d= 0
    # weist die materialien den faces
    for face in faces:
        face.material_index = d
        d+=1

    bm.to_mesh(cover_mesh)
    bm.free()

# Clears console


def clear():
    os.system('cls')


if (__name__ == "__main__"):
    clear()
    # requestAuthorization()
    # getSong("3I2Jrz7wTJTVZ9fZ6V3rQx")
    # getArtistsAlbums("26T3LtbuGT1Fu9m0eRq5X3")
    getSongImage("3I2Jrz7wTJTVZ9fZ6V3rQx")
