from nltk import word_tokenize
import useless_words
from nltk.stem import PorterStemmer
import time
from shutil import copyfile
from difflib import SequenceMatcher

# CONSTANTS
SIGN_PATH = "C:\\Users\\Shpoozipoo\\Desktop\\Signs"
SENTENCES_PATH = "C:\\Users\\Shpoozipoo\\Desktop\\Sentences"
DOWNLOAD_WAIT = 7
SIMILIARITY_RATIO = 0.9
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
    best_score = -1.
    closest_word_item = None
    for item in spinner:
        item_text = item.text
        # if stem == str(item_text).lower()[:len(stem)]:
        s = similar(word, str(item_text).lower())
        if s > best_score:
            best_score = s
            closest_word_item = item
            print(word, " ", str(item_text).lower())
            print("Score: " + str(s))
    if best_score < SIMILIARITY_RATIO:
        print(word + " not found in dictionary")
        return
    real_name = str(closest_word_item.text).lower()

    print("Downloading " + real_name + "...")
    closest_word_item.click()
    time.sleep(DOWNLOAD_WAIT)
    in_path = "C:\\Users\\Shpoozipoo\\Downloads\\" + real_name + ".swf"
    out_path = SIGN_PATH + "\\" + real_name + ".mp4"
    convert_file_format(in_path, out_path)
    browser.close()
    return real_name

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


def similar(a, b):
    # Returns a decimal representing the similiarity between the two strings.
    return SequenceMatcher(None, a, b).ratio()

def find_in_db(w):
    best_score = -1.
    best_vid_name = None
    for v in get_words_in_database():
        s = similar(w, v)
        if best_score < s:
            best_score =  s
            best_vid_name = v
    if best_score > SIMILIARITY_RATIO:
        return best_vid_name
# Get text
# text = str(input("Enter the text you would like to translate to pse \n"))
text = "You are a female and me am a mamal"
print("Text: " + text)
# Process text
words = process_text(text)
# Download words that have not been downloaded in previous sessions.
# words_in_db = get_words_in_database()
real_words = []
for w in words:
    real_name = find_in_db(w)
    if real_name:
        print(w + " is already in db as " + real_name)
        real_words.append(real_name)
    else:
        real_words.append(download_word_sign(w))
words = real_words
# Copy videos of signs used in this sentence into a folder
for w in words:
    copyfile(SIGN_PATH + "\\" + w + ".mp4", SENTENCES_PATH + "\\" + w + ".mp4")
# Concatenate videos and save output video to folder
merge_signs(words)

# Play the video
from os import startfile
startfile(SENTENCES_PATH + "\\Output\\out.mp4")