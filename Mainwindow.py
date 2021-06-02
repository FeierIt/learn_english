# -*- coding: utf-8 -*-
"""
Created on Mon Oct 28 20:15:30 2019

@author: Андрей
"""
from random import choice
import requests
import re
import sqlite3
import sys
import pyttsx3
from PyQt5 import uic
from PyQt5 import QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QApplication, QWidget, QMainWindow, QMessageBox,
                             QTableWidgetItem, QPushButton, QInputDialog, 
                             QErrorMessage)
from PyQt5.QtGui import QColor
engine = pyttsx3.init()
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[2].id)
URL = "https://translate.yandex.net/api/v1.5/tr.json/translate" 
KEY = ""  # Yandex translator API key 


class AddWidget(QWidget):  # Виджет добавления слов в БД
    def __init__(self):
        super().__init__()
        uic.loadUi('UI\AddWidget.ui', self)
        self.msg = QMessageBox()
        self.msg.setIcon(QMessageBox.Critical)
        self.msg.setWindowTitle("Error")
        self.error_dialog = QErrorMessage()
        self.setWindowTitle('Добавление')
        self._closable = True
        self.btn_variant.clicked.connect(self.translate)
        self.btn_change.clicked.connect(self.change)
        self.btn_add.clicked.connect(self.add)
        self.btn_question.clicked.connect(self.question)
        self.word = 'ru'
        self.translation = 'en'
        
    def question(self):  # Окно с текстом как разделить несколько переводов
        self.question = QMessageBox()
        self.question.setText("""Для добавления нескольких 
                              \nпереводов разделите их /""")
        self.question.setWindowTitle("Несколько переводов")
        self.question.show()
    
    def translate(self):  # Перевод слова
        word = self.line_word.text()
        if len(word) > 0:
            params = {"key": KEY, "text": word,
                      "lang": self.word + '-' + self.translation}
            response = requests.get(URL, params=params)
            json = response.json()
            self.line_translation.setText(json['text'][0])
        else:
            self.line_translation.setText('')
        
    def change(self):  # Меняет русккий и английский местами
        self.word, self.translation = self.translation, self.word
        text_word = self.line_word.text()
        text_translation = self.line_translation.text()
        self.line_translation.setText(text_word)
        self.line_word.setText(text_translation)
        if self.word == 'en':
            self.line_word.setPlaceholderText('Слово по английский')
        else:
            self.line_word.setPlaceholderText('Слово по русскии')
            
    def keyPressEvent(self, event):  
        # при нажатии enter вызывает функцию add
        if event.key() == Qt.Key_Enter or event.key() == 16777220:
            self.add()
    
    def add(self):  # Сохранить слово в БД
        db = sqlite3.connect('words.db')
        c = db.cursor()
        text_word = self.line_word.text().strip()
        text_translation = self.line_translation.text().strip()
        if len(text_word) > 0 and len(text_translation) > 0:
            text_word = [i.strip().lower() for i in text_word.split('/')]
            text_translation = [i.strip().lower() 
                                for i in text_translation.split('/')]
            correct = True
            true_text_ru = []
            true_text_en = []
            if self.word == 'ru':
                # Проверка корректности введеных данных
                for i in range(len(text_word)):
                    text_word[i] = [j.strip().lower() 
                                    for j in text_word[i].split()]
                    if not (all(re.match('^[а-яА-ЯёЁ]*$', x) is not None 
                                for x in text_word[i])):
                        correct = False
                    true_text_ru.append(' '.join(text_word[i]))
                for i in range(len(text_translation)):
                    text_translation[i] = [j.strip().lower()
                                           for j in 
                                           text_translation[i].split()]
                    if not (all(re.match('^[a-zA-Z]*$', x) is not None 
                                for x in text_translation[i])):
                        correct = False
                    true_text_en.append(' '.join(text_translation[i]))
            else:
                # Проверка корректности введеных данных
                for i in range(len(text_translation)):
                    text_translation[i] = [j.strip().lower() 
                                           for j in 
                                           text_translation[i].split()]
                    if not (all(re.match('^[а-яА-ЯёЁ]*$', x) is not None 
                                for x in text_translation[i])):
                        correct = False
                    true_text_ru.append(' '.join(text_translation[i]))
                for i in range(len(text_word)):
                    text_word[i] = [j.strip().lower() 
                                    for j in text_word[i].split()]
                    if not (all(re.match('^[a-zA-Z]*$', x) is not None 
                                for x in text_word[i])):
                        correct = False
                    true_text_en.append(' '.join(text_word[i]))
            if (correct):
                res = c.execute("SELECT * From Words")
                res = res.fetchall()
                flag = False
                for i in res:  # Проверяет есть ли слово в БД
                    if (
                        any(x in i[1].lower().split('/') 
                            for x in true_text_en) 
                        or any(x in i[2].lower().split('/') 
                               for x in true_text_ru)
                    ):
                        flag = True
                if flag:
                    self.msg.setText("Такое слово уже имеется")
                    self.msg.show()
                else:
                    # Добавление слова в БД
                    true_text_ru[0] = (true_text_ru[0][0].upper() + 
                                       true_text_ru[0][1:].lower())
                    true_text_en[0] = (true_text_en[0][0].upper() + 
                                       true_text_en[0][1:].lower())
                    c.execute("""INSERT INTO 
                              Words(Word_en, Word_ru, 
                              Correct_answers, Answers, Point) 
                              VALUES('{}', '{}', 0, 0, 0)""".format(
                              '/'.join(true_text_en), 
                              '/'.join(true_text_ru)))
            else:
                # Вызов ошибки
                self.msg.setText("Проверьте корректность \nвведенных данных")
                self.msg.show()
            db.commit()
            c.close()
            db.close()
            ex.list_widget.load_talbe()
        else:
            # Вызов ошибки
            self.msg.setText("Проверьте корректность \nвведенных данных")
            self.msg.show()
    
    def closeEvent(self, event):  # Закрытие окна
        if self._closable:
            super().closeEvent(event)
            ex.list_widget.close_active()
        else:
            event.ignore()
        
    def close_active(self):  # Делает окно закрываемым
        self._closable = True


class ChangeWidget(QWidget):  # Виджет изменения слова
    def __init__(self, number_position):
        super().__init__()
        uic.loadUi('UI\ChangeWidget.ui', self)
        self.msg = QMessageBox()
        self.msg.setIcon(QMessageBox.Critical)
        self.msg.setText("Проверьте корректность \nвведенных данных")
        self.msg.setWindowTitle("Error")
        self.error_dialog = QErrorMessage()
        self.setWindowTitle('Изменение')
        self._closable = True
        self._number_position = number_position
        db = sqlite3.connect('words.db')
        c = db.cursor()
        res = c.execute('SELECT * FROM Words')
        res = res.fetchall()
        self.id = res[self._number_position][0]
        self.line_en.setText(res[self._number_position][1])
        self.line_ru.setText(res[self._number_position][2])
        self.btn_save.clicked.connect(self.save_change)
        c.close()
        db.close()
    
    def keyPressEvent(self, event):
        # при нажатии enter вызывает функцию save_change
        if event.key() == Qt.Key_Enter or event.key() == 16777220:
            self.save_change()
    
    def save_change(self):  # Сохранение изменений
        text_en = self.line_en.text().strip().lower()
        text_ru = self.line_ru.text().strip().lower()
        if (len(text_en) > 0 and len(text_ru) > 0):
            text_en = [i.strip() for i in text_en.split('/')]
            text_ru = [i.strip() for i in text_ru.split('/')]
            correct = True
            correct_text_ru = []
            correct_text_en = []
            # Проверка корректности введеных данных
            for i in range(len(text_ru)):
                text_ru[i] = [j.strip().lower() for j in text_ru[i].split()]
                if not (all(re.match('^[а-яА-ЯёЁ]*$', x) is not None 
                            for x in text_ru[i])):
                    correct = False
                correct_text_ru.append(' '.join(text_ru[i]))
            for i in range(len(text_en)):
                text_en[i] = [j.strip().lower() for j in text_en[i].split()]
                if not (all(re.match('^[a-zA-Z]*$', x) is not None 
                            for x in text_en[i])):
                    correct = False
                correct_text_en.append(' '.join(text_en[i]))
            if (correct):
                correct_text_ru[0] = (correct_text_ru[0][0].upper() + 
                                      correct_text_ru[0][1:].lower())
                correct_text_en[0] = (correct_text_en[0][0].upper() + 
                                      correct_text_en[0][1:].lower())
                db = sqlite3.connect('words.db')
                c = db.cursor()
                # Обновление данных в БД
                c.execute("""UPDATE Words 
                          SET Word_en = '{}' 
                          WHERE id = '{}'""".format('/'.join(correct_text_en), 
                          str(self.id)))
                db.commit()
                c.execute("""UPDATE Words 
                          SET Word_ru = '{}' 
                          WHERE id = '{}'""".format('/'.join(correct_text_ru), 
                          str(self.id)))
                db.commit()
                c.close()
                db.close()
                ex.list_widget.load_talbe()
            else:
                # Вызов ошибки
                self.msg.show()
        else:
            # Вызов ошибки
            self.msg.show()
    
    def closeEvent(self, event):  # Закрытие окна
        if self._closable:
            super().closeEvent(event)
            ex.list_widget.close_active()
        else:
            event.ignore()
        
    def close_active(self):  # Делает окно закрываемым
        self._closable = True


class ListWidget(QWidget):  # Виджет таблицы слов
    def __init__(self):
        super().__init__()
        uic.loadUi('UI\ListWidget.ui', self)
        self.setWindowTitle('Словарь')
        self.load_talbe()
        self._closable = True
        self.btn_add_word.clicked.connect(self.add_word)
    
    def load_talbe(self):  # Загрузка слов в таблицу
        db = sqlite3.connect('words.db')
        c = db.cursor()
        res = c.execute('SELECT * FROM Words')
        res = res.fetchall()
        self.table_words.setRowCount(len(res))
        self.table_words.setColumnCount(5)
        self.table_words.setHorizontalHeaderLabels(['Английский', 
                                                    'Перевод', 
                                                    'Оценка знаний', 
                                                    '', ''])
        self.list_button_change = []
        self.list_button_delete = []
        for i in range(len(res)):
            for j in range(1, 3):
                item = QTableWidgetItem(res[i][j])
                item.setFlags(QtCore.Qt.ItemIsSelectable | 
                              QtCore.Qt.ItemIsEnabled)
                self.table_words.setItem(i, j - 1, item)
            rating = res[i][5]
            if rating <= 1 and rating >= 0.8:
                item = QTableWidgetItem('Отлично') 
                item.setForeground(QColor(0, 255, 0))
            elif rating < 0.8 and rating >= 0.6:
                item = QTableWidgetItem('Хорошо')
                item.setForeground(QColor(119, 255, 0))
            elif rating < 0.6 and rating >= 0.4:
                item = QTableWidgetItem('Средне') 
                item.setForeground(QColor(255, 255, 0))
            elif rating < 0.4 and rating >= 0.2:
                item = QTableWidgetItem('Так себе') 
                item.setForeground(QColor(255, 119, 0))
            elif rating < 0.2 and rating >= 0:
                item = QTableWidgetItem('Плохо') 
                item.setForeground(QColor(255, 0, 0))
            item.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
            self.table_words.setItem(i, 2, item)
            self.list_button_change.append(QPushButton("Изменить"))
            btn_delete = QPushButton('Удалить')
            btn_delete.setStyleSheet("""QPushButton 
                                     {background-color: rgb(234,43,43);}""")
            self.list_button_delete.append(btn_delete)
            self.table_words.setCellWidget(i, 3, self.list_button_change[i])
            self.table_words.setCellWidget(i, 4, self.list_button_delete[i])
            self.list_button_change[i].clicked.connect(self.change_word)
            self.list_button_delete[i].clicked.connect(self.delete_word)
        c.close()
        db.close()
    
    def change_word(self):  # Открыть виджет изменения слов
        self.window = ChangeWidget(
                self.list_button_change.index(self.sender()))
        self.window.show()
        self._closable = False
    
    def closeEvent(self, event):  # Закрытие окна
        if self._closable:
            super().closeEvent(event)
            ex.close_active()
        else:
            event.ignore()
        
    def close_active(self):  # Делает окно закрываемым
        self._closable = True
    
    def delete_word(self):  # Удаляет слово 
        db = sqlite3.connect('words.db')
        c = db.cursor()
        res = c.execute('SELECT * FROM Words')
        res = res.fetchall()
        index = self.list_button_delete.index(self.sender())
        del self.list_button_delete[index]
        del self.list_button_change[index]
        id_word = res[index][0]
        c.execute("DELETE from Words WHERE id = '" + str(id_word) + "'")
        db.commit()
        c.close()
        db.close()
        self.load_talbe()
    
    def add_word(self):  # Вызывает виджет добавляние слова 
        self.window = AddWidget()
        self.window.show()
        self._closable = False
      
        
class EnToRuWidget(QWidget):  # Виджет упражнения 
    def __init__(self, level, res):
        super().__init__()
        uic.loadUi('UI\EnToRuWidget.ui', self)
        self.setWindowTitle('Упражнение')
        self._level = level
        self.next = True
        self.flag = True
        self.word = choice(res)
        self.label_en.setText(self.word[1])
        self.btn_continue.clicked.connect(self.check_correct)
        self.btn_voice.clicked.connect(self.voice)
    
    def voice(self):  # Произносит слово 
        try:
            engine.say(self.word[1])
            engine.runAndWait()
        except RuntimeError:
            pass
    
    def keyPressEvent(self, event):
        # при нажатии enter вызывает функцию check_correct
        if event.key() == Qt.Key_Enter or event.key() == 16777220:
            self.check_correct()

    def check_correct(self):  # Проверяет правильный ли ответ дал пользователь
        if self.next:
            self.next = False
            db = sqlite3.connect('words.db')
            c = db.cursor()
            word_ru = self.line_ru.text().strip().lower()
            correct_word_ru = [i.lower() for i in self.word[2].split('/')]
            db = sqlite3.connect('words.db')
            c = db.cursor()
            c.execute("""UPDATE Words 
                      SET answers = answers + 1 
                      WHERE Word_en = '{}'""".format(self.word[1]))
            db.commit()
            if word_ru in correct_word_ru:
                ex.correct_answers()
                c.execute("""UPDATE Words 
                          SET correct_answers = correct_answers + 1 
                          WHERE Word_en = '{}'""".format(self.word[1]))
                db.commit()
                self.check_label.setStyleSheet(
                        """QLabel {background-color: rgb(184,242,139); 
                        color: rgb(88,167,0);}""")
                self.check_label.setText('Верно')
            else:
                ex.wrong_answers()
                self.check_label.setStyleSheet(
                        """QLabel {background-color: rgb(255,193,193); 
                        color: rgb(234,43,43);}""")
                self.check_label.setText('Неверно \nВерный ответ: ' + 
                                         self.word[2])
            c.close()
            db.close()
            db = sqlite3.connect('words.db')
            c = db.cursor()
            res = c.execute("""SELECT Correct_answers, answers FROM Words 
                            WHERE Word_en = '{}'""".format(self.word[1]))
            res = res.fetchall()
            point = res[0][0] / res[0][1]
            c.execute("""UPDATE Words 
                      SET point = {} 
                      WHERE Word_en = '{}'""".format(str(point), self.word[1]))
            db.commit()
            c.close()
            db.close()
        else:
            self.flag = False
            self.close()
            if self._level == 'learn':
                ex.next_question_learn()
            else:
                ex.next_question_repeat()
    
    def closeEvent(self, event):  # Закрытие окна
        if self.flag:
            ex.close_active()
            ex.wrong_answers()
            if self._level == 'learn':
                ex.next_question_learn()
            else:
                ex.next_question_repeat()
        else:
            ex.close_active()


class RuToEnWidget(QWidget):  # Виджет упражнения
    def __init__(self, level, res):
        super().__init__()
        uic.loadUi('UI\RuToEnWidget.ui', self)
        self.setWindowTitle('Упражнение')
        self.flag = True
        self.next = True
        self._level = level
        self.word = choice(res)
        self.label_ru.setText(self.word[2])
        self.btn_continue.clicked.connect(self.check_correct)
    
    def keyPressEvent(self, event):
        # при нажатии enter вызывает функцию check_correct
        if event.key() == Qt.Key_Enter or event.key() == 16777220:
            self.check_correct()

    def check_correct(self):  # Проверяет правильный ли ответ дал пользователь
        if self.next:
            self.next = False
            word_en = self.line_en.text().strip().lower()
            correct_word_en = [i.lower() for i in self.word[1].split('/')]
            db = sqlite3.connect('words.db')
            c = db.cursor()
            c.execute("""UPDATE Words 
                      SET answers = answers + 1 
                      WHERE Word_en = '{}'""".format(self.word[1]))
            db.commit()
            if word_en in correct_word_en:
                ex.correct_answers()
                c.execute("""UPDATE Words 
                          SET correct_answers = correct_answers + 1 
                          WHERE Word_en = '{}'""".format(self.word[1]))
                db.commit()
                self.check_label.setStyleSheet(
                        """QLabel {background-color: rgb(184,242,139); 
                        color: rgb(88,167,0);}""")
                self.check_label.setText('Верно')
            else:
                ex.wrong_answers()
                self.check_label.setStyleSheet(
                        """QLabel {background-color: rgb(255,193,193); 
                        color: rgb(234,43,43);}""")
                self.check_label.setText(
                        'Неверно \nВерный ответ: ' + self.word[1])
            c.close()
            db.close()
            db = sqlite3.connect('words.db')
            c = db.cursor()
            res = c.execute("""SELECT Correct_answers, answers FROM Words 
                            WHERE Word_en = '{}'""".format(self.word[1]))
            res = res.fetchall()
            point = res[0][0] / res[0][1]
            c.execute("""UPDATE Words 
                      SET point = {} 
                      WHERE Word_en = '{}'""".format(str(point), self.word[1]))
            db.commit()
            c.close()
            db.close()
        else:
            self.flag = False
            self.close()
            if self._level == 'learn':
                ex.next_question_learn()
            else:
                ex.next_question_repeat()

    def closeEvent(self, event):  # Закрытие окна
        if self.flag:
            ex.close_active()
            ex.wrong_answers()
            if self._level == 'learn':
                ex.next_question_learn()
            else:
                ex.next_question_repeat()
        else:
            ex.close_active()


class ListenWriteEnWidget(QWidget):
    def __init__(self, level, res):
        super().__init__()
        uic.loadUi('UI\ListenWriteWidget.ui', self)
        self.setWindowTitle('Упражнение')
        self._level = level
        self.next = True
        self.flag = True
        self.word = choice(res)
        self.btn_not_listen.clicked.connect(self.not_listen)
        self.btn_continue.clicked.connect(self.check_correct)
        self.btn_voice.clicked.connect(self.voice)
    
    def voice(self):  # Произносит слово 
        try:
            engine.say(self.word[1])
            engine.runAndWait()
        except RuntimeError:
            pass
    
    def keyPressEvent(self, event):
        # при нажатии enter вызывает функцию check_correct
        if event.key() == Qt.Key_Enter or event.key() == 16777220:
            self.check_correct()
        
    def not_listen(self):  # Пропускает упражнение
        self.flag = False
        self.close()
        if self._level == 'learn':
            ex.next_question_learn()
        else:
            ex.next_question_repeat()

    def check_correct(self):  # Проверяет правильный ли ответ дал пользователь
        if self.next:
            self.next = False
            word_en = self.line.text().strip().lower()
            correct_word_en = [i.lower() for i in self.word[1].split('/')]
            db = sqlite3.connect('words.db')
            c = db.cursor()
            c.execute("""UPDATE Words 
                      SET answers = answers + 1 
                      WHERE Word_en = '{}'""".format(self.word[1]))
            db.commit()
            if word_en in correct_word_en:
                ex.correct_answers()
                c.execute("""UPDATE Words 
                          SET correct_answers = correct_answers + 1 
                          WHERE Word_en = '{}'""" .format(self.word[1]))
                db.commit()
                self.check_label.setStyleSheet(
                        """QLabel {background-color: rgb(184,242,139); 
                        color: rgb(88,167,0);}""")
                self.check_label.setText('Верно')
            else:
                ex.wrong_answers()
                self.check_label.setStyleSheet(
                        """QLabel {background-color: rgb(255,193,193); 
                        color: rgb(234,43,43);}""")
                self.check_label.setText('Неверно \nВерный ответ: ' + 
                                         self.word[1])
            c.close()
            db.close()
            db = sqlite3.connect('words.db')
            c = db.cursor()
            res = c.execute("""SELECT Correct_answers, answers 
                            FROM Words
                            WHERE Word_en = '{}'""".format(self.word[1]))
            res = res.fetchall()
            point = res[0][0] / res[0][1]
            c.execute("""UPDATE Words 
                      SET point = {} 
                      WHERE Word_en = '{}'""".format(str(point), self.word[1]))
            db.commit()
            c.close()
            db.close()
        else:
            self.flag = False
            self.close()
            if self._level == 'learn':
                ex.next_question_learn()
            else:
                ex.next_question_repeat()
    
    def closeEvent(self, event):  # Закрытие окна
        if self.flag:
            ex.close_active()
            ex.wrong_answers()
            if self._level == 'learn':
                ex.next_question_learn()
            else:
                ex.next_question_repeat()
        else:
            ex.close_active()


class ListenWriteRuWidget(QWidget):
    def __init__(self, level, res):
        super().__init__()
        uic.loadUi('UI\istenWriteRuWidget.ui', self)
        self.setWindowTitle('Упражнение')
        self._level = level
        self.next = True
        self.flag = True
        self.word = choice(res)
        self.btn_not_listen.clicked.connect(self.not_listen)
        self.btn_continue.clicked.connect(self.check_correct)
        self.btn_voice.clicked.connect(self.voice)
    
    def voice(self):  # Произносит слово 
        try:
            engine.say(self.word[1])
            engine.runAndWait()
        except RuntimeError:
            pass
    
    def keyPressEvent(self, event):
        # при нажатии enter вызывает функцию check_correct
        if event.key() == Qt.Key_Enter or event.key() == 16777220:
            self.check_correct()
            
    def not_listen(self):  # Пропускает упражнение
        self.flag = False
        self.close()
        if self._level == 'learn':
            ex.next_question_learn()
        else:
            ex.next_question_repeat()
            
    def check_correct(self):  # Проверяет правильный ли ответ дал пользователь
        if self.next:
            self.next = False
            word_ru = self.line.text().strip().lower()
            correct_word_ru = [i.lower() for i in self.word[2].split('/')]
            db = sqlite3.connect('words.db')
            c = db.cursor()
            c.execute("""UPDATE Words 
                      SET answers = answers + 1 
                      WHERE Word_en = '{}'""" .format(self.word[1]))
            db.commit()
            if word_ru in correct_word_ru:
                ex.correct_answers()
                c.execute("""UPDATE Words 
                          SET correct_answers = correct_answers + 1 
                          WHERE Word_en = '{}'""".format(self.word[1]))
                db.commit()
                self.check_label.setStyleSheet(
                        """QLabel {background-color: rgb(184,242,139); 
                        color: rgb(88,167,0);}""")
                self.check_label.setText('Верно')
            else:
                ex.wrong_answers()
                self.check_label.setStyleSheet(
                        """QLabel {background-color: rgb(255,193,193); 
                        color: rgb(234,43,43);}""")
                self.check_label.setText('Неверно \nВерный ответ: ' + 
                                         self.word[2])
            c.close()
            db.close()
            db = sqlite3.connect('words.db')
            c = db.cursor()
            res = c.execute("""SELECT Correct_answers, answers 
                            FROM Words 
                            WHERE Word_en = '{}'""".format(self.word[1]))
            res = res.fetchall()
            point = res[0][0] / res[0][1]
            c.execute("""UPDATE Words 
                      SET point = {} 
                      WHERE Word_en = '{}'""".format(str(point), self.word[1]))
            db.commit()
            c.close()
            db.close()
        else:
            self.flag = False
            self.close()
            if self._level == 'learn':
                ex.next_question_learn()
            else:
                ex.next_question_repeat()
    
    def closeEvent(self, event):  # Закрытие окна
        if self.flag:
            ex.close_active()
            ex.wrong_answers()
            if self._level == 'learn':
                ex.next_question_learn()
            else:
                ex.next_question_repeat()
        else:
            ex.close_active()
            

class ResultsWidget(QWidget):  # Виджет, результаты пользователя 
    def __init__(self, wrong, correct):
        super().__init__()
        uic.loadUi('UI\ResultsWidget.ui', self)
        self.setWindowTitle('Результат')
        self.label_results.setText('Количество ответов: ' + 
                                   str(wrong + correct))
        self.label_correct.setText('Правильных ответов: ' + str(correct))
        self.label_wrong.setText('Неправильных ответов: ' + str(wrong))
    
    def closeEvent(self, event):  # Закрытие окна 
        ex.close_active()


class MainWindow(QMainWindow):  # Главное окно
    def __init__(self):
        super().__init__()
        uic.loadUi('UI\MainWindow.ui', self)
        self.msg = QMessageBox()
        self.msg.setIcon(QMessageBox.Critical)
        self.msg.setWindowTitle("Error")
        self.setWindowTitle('Learn English')
        self.list_question = [self.english_to_russian, self.russian_to_english,
                              self.listen_and_write_english,
                              self.listen_and_write_russian]
        self.btn_list_words.clicked.connect(self.list_words)
        self.btn_repeat_words.clicked.connect(self.repeat_words)
        self.btn_learn_words.clicked.connect(self.learn_words)
        self.btn_off_on.clicked.connect(self.off_on)
        self.list_question_random = None
        self.position = None
        self.flag = True
        self._closable = True
        
    def wrong_answers(self):  # Считает количество неправильных ответов
        self.number_wrong_answers += 1

    def correct_answers(self):  # Считает количество правильных ответов
        self.number_correct_answers += 1

    def closeEvent(self, event):  # Закрытие окна
        if self._closable:
            super().closeEvent(event)
        else:
            event.ignore()

    def list_words(self):  # Открывает виджет, список слов
        self.list_widget = ListWidget()
        self.list_widget.show()
        self._closable = False

    def english_to_russian(self, level):  # Открывает упражнение
        self.en_to_ru = EnToRuWidget(level, self.res)
        self.en_to_ru.show()
        self._closable = False

    def russian_to_english(self, level):  # Открывает упражнение
        self.ru_to_en = RuToEnWidget(level, self.res)
        self.ru_to_en.show()
        self._closable = False
        
    def listen_and_write_english(self, level):  # Открывает упражнение
        self.listen_write_en = ListenWriteEnWidget(level, self.res)
        self.listen_write_en.show()
        self._closable = False
    
    def listen_and_write_russian(self, level):  # Открывает упражнение
        self.listen_write_ru = ListenWriteRuWidget(level, self.res)
        self.listen_write_ru.show()
        self._closable = False
    
    def off_on(self):  # Отключает задачи на аудирование
        if len(self.list_question) == 4:
            self.list_question = [self.english_to_russian, 
                                  self.russian_to_english]
            self.btn_off_on.setStyleSheet(
                    """QPushButton {background-color: rgb(0,176,0); 
                    color: rgb(255,255,255);}""")
            self.btn_off_on.setText("Включить упражения \nна аудирование")
        else:
            self.list_question = [self.english_to_russian, 
                                  self.russian_to_english,
                                  self.listen_and_write_english,
                                  self.listen_and_write_russian]
            self.btn_off_on.setStyleSheet(
                    """QPushButton {background-color: rgb(176,0,0); 
                    color: rgb(255,255,255);}""")
            self.btn_off_on.setText("Отключить упражения \nна аудирование")
    
    def results(self):  # Открывает результаты 
        self.results_widget = ResultsWidget(self.number_wrong_answers, 
                                            self.number_correct_answers)
        self.results_widget.show()
        self._closable = False
    
    def learn_words(self):  # Генерация упражнений для изучения
        db = sqlite3.connect('words.db')
        c = db.cursor()
        self.res = c.execute('SELECT * FROM Words WHERE Point < 0.4')
        self.res = self.res.fetchall()
        c.close()
        db.close()
        if len(self.res) > 0:
            if self.flag:
                number, okBtnPressed = QInputDialog.getInt(
                        self, "Введите количество слов",
                        "Сколько слов вы хотите изучить?",
                        5, 3, 20, 1)
                if okBtnPressed:
                    # При нажатии на OK начинает генерировать упражнения
                    self.number_correct_answers = 0
                    self.number_wrong_answers = 0
                    self.number = number
                    self.position = 0
                    self.list_question_random = []
                    for i in range(number):
                        self.list_question_random.append(
                                choice(self.list_question))
                    self.next_question_learn()
            else:
                # Вызывает ошибку
                self.msg.setText("""Закончите упражнение 
                                 \nчтобы начать следующее""")
                self.msg.show()
        else:
            # Вызывает ошибку
            self.msg.setText("Нет слов для изучения")
            self.msg.show()

    def next_question_learn(self):  
        # Вызывает следующее упражнение для изучения
        if self.position >= self.number:
            self.results()
            self.flag = True
        else:
            self.flag = False
            self.list_question_random[self.position]('learn')
            self.position += 1

    def repeat_words(self):  # Генерация упражнений для повторения
        db = sqlite3.connect('words.db')
        c = db.cursor()
        self.res = c.execute('SELECT * FROM Words WHERE Point >= 0.4')
        self.res = self.res.fetchall()
        c.close()
        db.close()
        if len(self.res) > 0:
            if self.flag:
            
                number, okBtnPressed = QInputDialog.getInt(
                        self, "Введите количество слов",
                        "Сколько слов вы хотите повторить?",
                        5, 3, 20, 1)
                if okBtnPressed:
                    # При нажатии на OK начинает генерировать упражнения
                    self.number_correct_answers = 0
                    self.number_wrong_answers = 0
                    self.number = number
                    self.position = 0
                    self.list_question_random = []
                    for i in range(number):
                        self.list_question_random.append(
                                choice(self.list_question))
                    self.next_question_repeat()
            else:
                # Вызывает ошибку
                self.msg.setText("""Закончите упражнение 
                                 \nчтобы начать следующее""")
                self.msg.show()
        else:
            # Вызывает ошибку
            self.msg.setText("Нет слов для повторения")
            self.msg.show()

    def next_question_repeat(self):  
        # Вызывает следующее упражнение для повторения
        if self.position >= self.number:
            self.results()
            self.flag = True
        else:
            self.flag = False
            self.list_question_random[self.position]('repeat')
            self.position += 1
            
    def close_active(self):  # Делает окно закрываемым 
        self._closable = True


app = QApplication(sys.argv)
ex = MainWindow()
ex.show()
sys.exit(app.exec_())
