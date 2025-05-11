import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import re
import pymorphy2
from nltk.corpus import stopwords
from collections import Counter
import matplotlib.pyplot as plt
import json
import os

# Підготовка
morph = pymorphy2.MorphAnalyzer(lang='uk')

# Шлях до словників
POSITIVE_WORDS_FILE = "positive_words.json"
NEGATIVE_WORDS_FILE = "negative_words.json"

# Завантаження словників
def load_words(filename):
    if os.path.exists(filename):
        with open(filename, 'r', encoding='utf-8') as f:
            return set(json.load(f))
    return set()

positive_words = load_words(POSITIVE_WORDS_FILE)
negative_words = load_words(NEGATIVE_WORDS_FILE)

# Збереження словників
def save_words(words, filename):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(sorted(list(words)), f, ensure_ascii=False)

# Очистка і лематизація
def preprocess(text):
    text = re.sub(r'[^\w\s]', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    text = text.lower()
    words = text.split()
    lemmatized = [morph.parse(word)[0].normal_form for word in words if word.isalpha()]
    return lemmatized

# Аналіз одного тексту
def analyze_text(words):
    pos = [w for w in words if w in positive_words]
    neg = [w for w in words if w in negative_words]
    r = len(pos) + len(neg)
    t = len(words)
    if r == 0 or t == 0:
        y = 0
    else:
        y = ((len(pos) - len(neg)) / r) * (r / t)

    sentiment = "нейтральний"
    if y > 0.01:
        sentiment = "позитивний"
    elif y < -0.01:
        sentiment = "негативний"

    return pos, neg, round(y, 4), sentiment

# Обробка файлу
def process_file():
    file_path = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt")])
    if not file_path:
        return

    with open(file_path, 'r', encoding='utf-8') as f:
        texts = f.read().strip().split("\n\n")  # Заміняємо на постовий режим (розділяємо по порожніх рядках)

    output.delete('1.0', tk.END)
    global_total_pos = 0
    global_total_neg = 0
    all_results = []

    print("Всього постів:", len(texts))  # Показуємо кількість постів у консолі

    for idx, post in enumerate(texts):
        words = preprocess(post)
        pos, neg, score, sentiment = analyze_text(words)
        global_total_pos += len(pos)
        global_total_neg += len(neg)

        result = f"Текст {idx+1}:\n"
        result += f"Позитивні слова: {', '.join(pos) if pos else 'немає'}\n"
        result += f"Негативні слова: {', '.join(neg) if neg else 'немає'}\n"
        result += f"Коефіцієнт Яніса: {score} → {sentiment}\n\n"
        output.insert(tk.END, result)
        all_results.append(result)

    output.insert(tk.END, f"\nЗагалом позитивних слів: {global_total_pos}\n")
    output.insert(tk.END, f"Загалом негативних слів: {global_total_neg}\n")
    last_results.clear()
    last_results.extend(all_results)
    last_results.append(f"\nЗагалом позитивних: {global_total_pos}, негативних: {global_total_neg}")

def save_results():
    file_path = filedialog.asksaveasfilename(defaultextension=".txt")
    if not file_path:
        return
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(last_results))
    messagebox.showinfo("Збережено", "Результати збережено!")

def add_word():
    word = word_entry.get().strip().lower()
    if not word:
        return
    category = var.get()
    lemma = morph.parse(word)[0].normal_form
    if category == "Позитивне":
        positive_words.add(lemma)
        save_words(positive_words, POSITIVE_WORDS_FILE)
    else:
        negative_words.add(lemma)
        save_words(negative_words, NEGATIVE_WORDS_FILE)
    word_entry.delete(0, tk.END)
    messagebox.showinfo("Додано", f"Слово '{lemma}' додано до {category.lower()} слів.")

def show_plot():
    labels = ['Позитивні', 'Негативні']
    values = [sum(1 for word in positive_words), sum(1 for word in negative_words)]
    plt.bar(labels, values, color=['green', 'red'])
    plt.title("Кількість слів у словнику")
    plt.show()

# GUI
root = tk.Tk()
root.title("Емоційний аналіз постів")
root.geometry("800x700")

frame = tk.Frame(root)
frame.pack(pady=10)

tk.Button(frame, text="Завантажити текстовий файл", command=process_file).grid(row=0, column=0, padx=5)
tk.Button(frame, text="Зберегти результати", command=save_results).grid(row=0, column=1, padx=5)
tk.Button(frame, text="Побудувати графік", command=show_plot).grid(row=0, column=2, padx=5)

word_entry = tk.Entry(frame, width=20)
word_entry.grid(row=1, column=0, pady=10)
var = tk.StringVar(value="Позитивне")
tk.OptionMenu(frame, var, "Позитивне", "Негативне").grid(row=1, column=1)
tk.Button(frame, text="Додати слово", command=add_word).grid(row=1, column=2)

output = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=100, height=30)
output.pack(pady=10)

last_results = []

root.mainloop()
