import webbrowser
import numpy as np
import cv2
import bpy
import requests
import os
#import sysimage.png
#sys.path.append('c:\\Users\\sanok\\Documents\\Semester5\\Repo\\DaVeMePro_Endabgabe')

bl_info = {
    "name": "Basic Addon",
    "author": "Samuel Kasper, Alexander Reiprich, David Niemann, Daniel Meisler",
    "version": (1, 0),
    "blender": (2, 91, 0),
    "category": "Add Mesh",
}


def main():
    bpy.ops.object.select_all(action='SELECT')  # selektiert alle Objekte
    # löscht selektierte objekte
    bpy.ops.object.delete(use_global=False, confirm=False)
    bpy.ops.outliner.orphans_purge()  # löscht überbleibende Meshdaten etc.
    Method()


CLIENT_ID = "56651af3c4134034b9977c0a650b2cdf"
CLIENT_SECRET = "ba05f9e81dbc4443857aa9f3afcfc88b"
REDIRECT_URL = "http://127.0.0.1:5555/callback.html"
# DO NOT PUSH WHEN USER_CODE IS NOT ""!!!
USER_CODE = ""

AUTH_URL = "https://accounts.spotify.com/api/token"
CLIENT_AUTH_URL = "https://accounts.spotify.com/authorize"
BASE_URL = "https://api.spotify.com/v1/"

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


class Method():
    def __init__(self):
        print("Init")

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
        #getSong(track_id)
        r = requests.get(BASE_URL + "tracks/" + track_id, headers=headers)
        d = r.json()

        # Get image part
        cover_image = requests.get(d["album"]["images"][0]['url'])

        # with open("coverImage.png", 'wb') as f:
        #    f.write(cover_image.content)

        img_string = np.frombuffer(cover_image.content, np.uint8)
        img = cv2.imdecode(img_string, cv2.IMREAD_COLOR)

        # Get Pixalized
        #img = cv2.imread('coverImage.png')
        resized = cv2.resize(img, (25, 25), interpolation=cv2.INTER_LINEAR)
        resized = cv2.resize(img, (50, 50), interpolation=cv2.INTER_NEAREST)
        cv2.namedWindow('img', cv2.WINDOW_NORMAL)
        cv2.resizeWindow('img', 500, 500)
        cv2.imshow('img', resized)
        cv2.waitKey(0)

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

            trim_name = album_name.split(
                '(')[0].strip()  # Filter out duplicates
            if trim_name.upper() in albums:
                continue

            albums.append(trim_name.upper())

            print(album_name, "---", album["release_date"])

        print()

    # Clears console
    def clear():
        os.system('cls')


class AutostartThing(bpy.types.Operator):
    bl_idname = "object.test"
    bl_label = "BasicAddonTest"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        main()
        return {'FINISHED'}


def register():
    bpy.utils.register_class(AutostartThing)


def unregister():
    bpy.utils.unregister_class(AutostartThing)


if __name__ == "__main__":
    register()
