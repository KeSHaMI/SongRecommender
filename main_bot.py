import telebot
from telebot import types
import pymongo
import re
import string
import pandas as pd
import pickle
from config import password
from config import TOKEN

"""This bot based fully on callbacks(first time) 
   also this bot suffers from common variables(I invented how to deal with it in other bots but for simplicity don't use it here)
   It's probably a good idea to use OOP here but I like spaghetti 
"""

#       #       #       #       #   Variables   #       #       #       #       #
cluster = pymongo.MongoClient(f'mongodb+srv://Kesha:{password}@song-recommender-bvyjq.mongodb.net/test?retryWrites=true&w=majority')

db_songs = cluster['Songs_full']
collection_songs = db_songs['Songs']

db = cluster['Telebot']
collection = db['Song_bot']

db_rec = cluster['Song_Recc']
collection_rec = db_rec['Songs']

with open('singers.txt', 'r', encoding='utf-8') as f:
    all_artists = f.read().splitlines()

all_artists = [artist.replace('\xa0', '') for artist in all_artists]

bot = telebot.TeleBot(TOKEN)

df = pd.read_csv('processed_lyrics_genres.csv')
indices = pd.Series(df.index, index=df['Song']).drop_duplicates()
with open('sig_kernel', 'rb') as f:
    kernel = pickle.load(f)

#       #       #       #       #   Functions   #       #       #       #       #
@bot.message_handler(commands=['start'])
def start(message):
    #If user not in database adding him
    if not collection.find_one({'_id': message.chat.id}):
        collection.insert_one({'_id': message.chat.id,
                               'name': message.from_user.first_name})

    markup = types.InlineKeyboardMarkup(row_width=1)

    but1 = types.InlineKeyboardButton('Выбрать песню', callback_data='all_songs')
    but2 = types.InlineKeyboardButton('Рекомендация песни '
                                      'по тексту(beta)', callback_data='recommend')

    markup.add(but1, but2)

    bot.send_message(message.chat.id, 'Вас приветствует бот Song Recommender! Бот с более 250 000 песен в базе данных\n'
                                      'Здесь вы можете посмотреть текст ваших любимых песен(надеюсь), а также получить рекомедации к прослушыванию на основании текста выбраной песни',
                     reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == 'recommend')
def recommend(call):
    markup = types.InlineKeyboardMarkup()

    but1 = types.InlineKeyboardButton('Noize MC', callback_data='noizzz')
    but2 = types.InlineKeyboardButton('Anacondaz', callback_data='anacondazzz')

    markup.add(but1, but2)

    bot.send_message(call.message.chat.id, 'Выберите исполнителя:', reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == 'noizzz')
def songs_noize(call):
    noiz_index = 0
    buts = []
    songs_noiz = []

    markup = types.InlineKeyboardMarkup(row_width=2)

    results = collection_rec.find({'Singer' : 'Noize MC'})
    for result in results:
        songs_noiz.append(result['Song'])

    songs_noiz = sorted(songs_noiz)
    for song in songs_noiz:
        buts.append(types.InlineKeyboardButton(song, callback_data='n{}'.format(songs_noiz.index(song))))

    markup.add(*buts[noiz_index:noiz_index+10])

    but1 = types.InlineKeyboardButton('➡', callback_data='plus_s_r_n')
    but2 = types.InlineKeyboardButton('⬅', callback_data='minus_s_r_n')

    markup.add(but2, but1)

    bot.edit_message_text(message_id=call.message.message_id, chat_id=call.message.chat.id,
                          text='Выберите песню:')
    bot.edit_message_reply_markup(message_id=call.message.message_id, chat_id=call.message.chat.id, reply_markup=markup)

    @bot.callback_query_handler(func=lambda call: call.data == 'plus_s_r_n' or call.data == 'minus_s_r_n')
    def update_songs_noiz(call):
        nonlocal noiz_index
        markup = types.InlineKeyboardMarkup(row_width=2)

        if call.data == 'plus_s_r_n':
            noiz_index += 10
        else:
            noiz_index -= 10


        if (noiz_index + 10) >= (len(buts) + 10):
            noiz_index = len(buts) - 10
        elif noiz_index < 0:
            noiz_index = 0

        markup.add(*buts[noiz_index:noiz_index + 10])


        but1 = types.InlineKeyboardButton('➡', callback_data='plus_s_r_n')
        but2 = types.InlineKeyboardButton('⬅', callback_data='minus_s_r_n')

        markup.add(but2, but1)

        bot.edit_message_reply_markup(message_id=call.message.message_id, chat_id=call.message.chat.id, reply_markup=markup)

        @bot.callback_query_handler(func=lambda call: re.match('n[0-9]+', call.data))
        def give_recommendations(call):
            call.data = call.data.replace('n', '')
            bot.send_message(call.message.chat.id, 'Рекомендации к песне Noize MC {} \n{}'.format(songs_noiz[int(call.data)],
                             get_recommendations(songs_noiz[int(call.data)])))
            try:
                bot.send_message(call.message.chat.id, '{}'.format(list(collection_songs.find({'$and': [{'Singer' : 'Noize MC'},
                                                             {'Song' : songs_noiz[int(call.data)]}]}))[0]['Lyrics']), reply_markup=markup)
            except:                                                                             #)))))
                bot.send_message(call.message.chat.id, 'К сожалению к этой песне нет текста :(', reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == 'anacondazzz')
def songs_anacondaz(call):
    anacondaz_index = 0
    buts = []
    songs_anacondaz = []

    markup = types.InlineKeyboardMarkup(row_width=2)

    results = collection_rec.find({'Singer' : 'Anacondaz'})
    for result in results:
        songs_anacondaz.append(result['Song'])

    songs_anacondaz = sorted(songs_anacondaz)
    for song in songs_anacondaz:
        buts.append(types.InlineKeyboardButton(song, callback_data='a{}'.format(songs_anacondaz.index(song))))

    markup.add(*buts[anacondaz_index:anacondaz_index+10])

    but1 = types.InlineKeyboardButton('➡', callback_data='plus_s_r_a')
    but2 = types.InlineKeyboardButton('⬅', callback_data='minus_s_r_a')

    markup.add(but2, but1)

    bot.edit_message_text(message_id=call.message.message_id, chat_id=call.message.chat.id,
                          text='Выберите песню:')
    bot.edit_message_reply_markup(message_id=call.message.message_id, chat_id=call.message.chat.id, reply_markup=markup)

    @bot.callback_query_handler(func=lambda call: call.data == 'plus_s_r_a' or call.data == 'minus_s_r_a')
    def update_songs_anacondaz(call):
        nonlocal anacondaz_index

        if call.data == 'plus_s_r_a':
            anacondaz_index += 10
        else:
            anacondaz_index -= 10

        markup = types.InlineKeyboardMarkup(row_width=2)

        if (anacondaz_index + 10) >= (len(buts) + 10):
            anacondaz_index = len(buts) - 10
        elif anacondaz_index < 0:
            anacondaz_index = 0

        markup.add(*buts[anacondaz_index:anacondaz_index + 10])

        but1 = types.InlineKeyboardButton('➡', callback_data='plus_s_r_a')
        but2 = types.InlineKeyboardButton('⬅', callback_data='minus_s_r_a')

        markup.add(but2, but1)

        bot.edit_message_reply_markup(message_id=call.message.message_id, chat_id=call.message.chat.id, reply_markup=markup)

        @bot.callback_query_handler(func=lambda call: re.match('a[0-9]+', call.data))
        def give_recommendations_anacondaz(call):
            call.data = call.data.replace('a', '')
            bot.send_message(call.message.chat.id, ' Рекомендации к песне Anacondaz: {}\n{}\n'.format(
                songs_anacondaz[int(call.data)] ,get_recommendations(songs_anacondaz[int(call.data)])))
            try:
                bot.send_message(call.message.chat.id, '{}'.format(list(collection_songs.find({'$and': [{'Singer': 'Anacondaz'},
                                                 {'Song' : songs_anacondaz[int(call.data)]}]}))[0]['Lyrics']), reply_markup=markup)
            except:                                                                     #))))))
                bot.send_message(call.message.chat.id, 'К сожалению к этой песне нет текста :(', reply_markup=markup)


def get_recommendations(title, kernel=kernel, indices=indices):
    """Detailed function description is in main.py
    Here only string formatting added"""
    idx = indices[title]

    sim_scores = list(enumerate(kernel[idx]))

    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)

    sim_scores = sim_scores[1:11]

    movie_indices = [i[0] for i in sim_scores]

    recommendations = df[['Song', 'Singer']].iloc[movie_indices].to_string(index=False, header=False).replace('\xa0', ' ').split('\n')

    all_songs_rec = [each.strip() for each in recommendations]

    output = ['{}  -   {}'.format(each[:-9], each[-9:]) for each in all_songs_rec]

    return '\n'.join(output)

@bot.callback_query_handler(func=lambda call: call.data == 'all_songs')
def artist_selection_all(call):
    markup = types.InlineKeyboardMarkup()

    but1 = types.InlineKeyboardButton('Английский', callback_data='english')
    but2 = types.InlineKeyboardButton('Русский', callback_data='russian')

    markup.add(but1, but2)

    bot.send_message(call.message.chat.id, 'Выберите язык имени артиста(например Noize MC - английский)', reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == 'english')
def artist_en(call):
    markup = types.InlineKeyboardMarkup(row_width=5)
    buts = []

    for letter in string.ascii_uppercase:
        but = types.InlineKeyboardButton(letter, callback_data=f'{letter}')
        buts.append(but)

    markup.add(*buts)
    bot.edit_message_text(message_id=call.message.message_id, chat_id=call.message.chat.id,
                          text='Выберите букву на которую начинаеться имя' )
    bot.edit_message_reply_markup(message_id=call.message.message_id, chat_id=call.message.chat.id, reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data == 'russian')
def artist_ru(call):
    markup = types.InlineKeyboardMarkup(row_width=5)
    buts = []
    a = ord('а') #Literally a

    for letter in ''.join([chr(i).upper() for i in range(a,a+32)]):
        but = types.InlineKeyboardButton(letter, callback_data=f'{letter}')
        buts.append(but)

    markup.add(*buts)

    bot.edit_message_text(message_id=call.message.message_id, chat_id=call.message.chat.id,
                          text='Выберите букву на которую начинаеться имя' )
    bot.edit_message_reply_markup(message_id=call.message.message_id, chat_id=call.message.chat.id, reply_markup=markup)


@bot.callback_query_handler(func=lambda call: re.match('^\w{1}$', call.data))
def lettered_artist(call):
    artists_index = 0

    markup = types.InlineKeyboardMarkup(row_width=3)

    buts = []
    pattern = re.compile('^{}'.format(call.data))
    artists = []

    results = collection_songs.find({'Singer': pattern})
    for result in results:
        artists.append(result['Singer'])

    for artist in sorted(list(set(artists))):
        but = types.InlineKeyboardButton(artist, callback_data='{}'.format(artist))
        buts.append(but)

    markup.add(*buts[artists_index : artists_index+9])


    but1 = types.InlineKeyboardButton('➡', callback_data='plus')
    but2 = types.InlineKeyboardButton('⬅', callback_data='minus')
    but3 = types.InlineKeyboardButton('𝄞', callback_data='NONE')

    markup.add(but2, but3, but1)

    bot.edit_message_text(message_id=call.message.message_id, chat_id=call.message.chat.id,
                          text='Выберите исполнителя:' )
    bot.edit_message_reply_markup(message_id=call.message.message_id, chat_id=call.message.chat.id, reply_markup=markup)

    @bot.callback_query_handler(func=lambda call: call.data == 'plus' or call.data == 'minus')
    def update_artists(call):
        nonlocal artists_index

        if call.data == 'plus':
            artists_index += 9
        else:
            artists_index -= 9

        markup = types.InlineKeyboardMarkup(row_width=3)

        if (artists_index + 9) >= len(buts):
            artists_index = len(buts) - 9
        elif artists_index < 0:
            artists_index = 0
        markup.add(*buts[artists_index: artists_index + 9])

        but1 = types.InlineKeyboardButton('➡', callback_data='plus')
        but2 = types.InlineKeyboardButton('⬅', callback_data='minus')
        but3 = types.InlineKeyboardButton('𝄞', callback_data='NONE')

        markup.add(but2, but3, but1)

        bot.edit_message_reply_markup(message_id=call.message.message_id, chat_id=call.message.chat.id, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data in all_artists)
def artist_songs(call):
    #Temporary saving artist in database for more explicit search(different artists can have songs with same names)
    collection.update({'_id': call.message.chat.id}, {'$set': {'Singer': call.data}})

    markup = types.InlineKeyboardMarkup(row_width=2)
    song_index = 0
    buts_songs = []
    songs = []

    for result in collection_songs.find({'Singer': call.data}):
        songs.append(result['Song'])

    songs = sorted(songs)

    for i, song in enumerate(songs):
        buts_songs.append(types.InlineKeyboardButton('{}'.format(song), callback_data='song{}'.format(i)))

    markup.add(*buts_songs[song_index:song_index+10])

    but1 = types.InlineKeyboardButton('➡', callback_data='plus_s')
    but2 = types.InlineKeyboardButton('⬅', callback_data='minus_s')

    markup.add(but2, but1)

    bot.edit_message_text(message_id=call.message.message_id, chat_id=call.message.chat.id,
                          text='Выберите песню:')
    bot.edit_message_reply_markup(message_id=call.message.message_id, chat_id=call.message.chat.id, reply_markup=markup)


    @bot.callback_query_handler(func=lambda call: call.data == 'plus_s' or call.data == 'minus_s')
    def update_songs(call):
        nonlocal song_index

        markup = types.InlineKeyboardMarkup(row_width=2)

        if call.data == 'plus_s':
            song_index += 10
        else:
            song_index -= 10

        if (song_index + 10) >= (len(buts_songs)+10):
            song_index = len(buts_songs) - 10
        elif song_index < 0:
            song_index = 0

        markup.add(*buts_songs[song_index:song_index + 10])

        but1 = types.InlineKeyboardButton('➡', callback_data='plus_s')
        but2 = types.InlineKeyboardButton('⬅', callback_data='minus_s')

        markup.add(but2, but1)

        bot.edit_message_reply_markup(message_id=call.message.message_id, chat_id=call.message.chat.id, reply_markup=markup)

        @bot.callback_query_handler(func=lambda call: call.data.startswith('song'))
        def show_lyrics(call):
            nonlocal song_index
            for res in collection.find({'_id': call.message.chat.id}):
                singer = res['Singer']

            pattern = re.compile('{}'.format(songs[int(call.data[4:])]))

            markup = types.InlineKeyboardMarkup(row_width=2)
            if call.data == 'plus_s':
                song_index += 10
            else:
                song_index -= 10

            if (song_index + 10) >= (len(buts_songs) + 10):
                song_index = len(buts_songs) - 10
            elif song_index < 0:
                song_index = 0

            markup.add(*buts_songs[song_index:song_index + 10])

            but1 = types.InlineKeyboardButton('➡', callback_data='plus_s')
            but2 = types.InlineKeyboardButton('⬅', callback_data='minus_s')

            markup.add(but2, but1)

            try:
                bot.send_message(call.message.chat.id, '{}'.format(list(collection_songs.find({'$and': [{'Song': pattern},
                                                {'Singer': singer}]}))[0]['Lyrics']), reply_markup=markup)
            except:
                bot.send_message(call.message.chat.id, 'К сожалению к этой песне нет текста :( \n'
                                                       'Или создатель криворукий? 🤔')


bot.polling(none_stop=True)
