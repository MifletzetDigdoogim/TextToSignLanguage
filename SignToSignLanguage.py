from nltk import word_tokenize
import useless_words
from nltk.stem import PorterStemmer
import time
from shutil import copyfile

# CONSTANTS
SIGN_PATH = "C:\\Users\\Shpoozipoo\\Desktop\\Signs"
SENTENCES_PATH = "C:\\Users\\Shpoozipoo\\Desktop\\Sentences"
DOWNLOAD_WAIT = 7
# Get words
def download_word_sign(word):
    from selenium import webdriver
    browser = webdriver.Firefox()
    browser.get("http://www.aslpro.com/cgi-bin/aslpro/aslpro.cgi")
    first_letter = word[0]
    letters = browser.find_elements_by_xpath('//a[@class="sideNavBarUnselectedText"]')
    for letter in letters:
        if first_letter == str(letter.text).strip().lower():
            # print("Downloading " + letter.text + "...")
            letter.click()
            time.sleep(2)
            break
    # from nltk.stem import PorterStemmer
    # ps = PorterStemmer()
    # stem = ps.stem(word)
    # Show drop down menu ( Spinner )
    spinner = browser.find_elements_by_xpath("//option")
    found = False
    for item in spinner:
        item_text = item.text
        # if stem == str(item_text).lower()[:len(stem)]:
        if word == str(item_text).lower():
            found = True
            print("Downloading " + word + "...")
            item.click()
            time.sleep(DOWNLOAD_WAIT)
            break
    if not found:
        print(word + " not found in dictionary")
        return
    in_path = "C:\\Users\\Shpoozipoo\\Downloads\\" + word + ".swf"
    out_path = SIGN_PATH + "\\" + word + ".mp4"
    convert_file_format(in_path, out_path)
    browser.close()

def convert_file_format(in_path, out_path):
    # Converts .swf filw to .mp4 file and saves new file at out_path
    from ffmpy import FFmpeg

    ff = FFmpeg(
    inputs = {in_path: None},
    outputs = {out_path: None})
    ff.run()

def get_words_in_database():
    import os
    vids = os.listdir(SIGN_PATH)
    vid_names = [v[:-4] for v in vids]
    return vid_names

def process_text(text):
    # Split sentence into words
    words = word_tokenize(text)
    # Remove all meaningless words
    usefull_words = [str(w).lower() for w in words if w.lower() not in set(useless_words.words())]

    # TODO: Add stemming to words and change search accordingly. Ex: 'talking' will yield 'talk'.

    # TODO: Create Sytnax such that the words will be in ASL order as opposed to PSE.

    return usefull_words


def merge_signs(words):
    # Write a text file containing all the paths to each video
    with open("vidlist.txt", 'w') as f:
        for w in words:
            f.write("file '" + SENTENCES_PATH + "\\" + w + ".mp4'\n")
    command = "ffmpeg -f concat -safe 0 -i vidlist.txt -c copy output.mp4"
    import shlex
    # Splits the command into pieces in order to feed the command line
    args = shlex.split(command)
    import subprocess
    subprocess.Popen(args)
    copyfile("output.mp4",SENTENCES_PATH + "\\Output\\out.mp4") # copyfile(src, dst)
    # remove the temporary file (it used to ask me if it should override previous file).
    import os
    os.remove("output.mp4")

def in_database(w):
    db_list = get_words_in_database()
    from nltk.stem import PorterStemmer
    ps = PorterStemmer()
    s = ps.stem(w)
    for word in db_list:
        if s == word[:len(s)]:
            return True
    return False

# Get text
# text = str(input("Enter the text you would like to translate to pse \n"))
text = "me want to go to israel"
print("Text: " + text)
# Process text
words = process_text(text)
# Download words that have not been downloaded in previous sessions.
words_in_db = get_words_in_database()
for w in words:
    if w in get_words_in_database():
        print(w + " is already in db")
    else:
        download_word_sign(w)
# Copy videos of signs used in this sentence into a folder
for w in words:
    copyfile(SIGN_PATH + "\\" + w + ".mp4", SENTENCES_PATH + "\\" + w + ".mp4")
# Concatenate videos and save output video to folder
merge_signs(words)

# Play the video
from os import startfile
startfile(SENTENCES_PATH + "\\Output\\out.mp4")