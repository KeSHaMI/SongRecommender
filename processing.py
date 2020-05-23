import pandas as pd
import re
def process_songs(text):
    """If song name is russian it has translation in parentheses.
    This function goal is to remove them"""
    if re.match('^[A-Za-z]', text) or re.match('[1-9]|[+-]', text):
        return text
    else:
        try:
            return text.replace(re.search('\((.*)\)', text).group(0), '')
        except:
            return text
df = pd.read_csv('D:\CODE\Song recomender\songs_dataset.csv')

def del_whitespace(text):
    if len(text) == 0:
        return text
    if text[-1] == ' ':
        text = text[:-1]
    return text
df['Song'] = df.Song.apply(process_songs).apply(del_whitespace)


df['Singer'] = df.Singer.str.replace('\xa0', ' ')

df.to_csv('new_songs_dataset.csv')