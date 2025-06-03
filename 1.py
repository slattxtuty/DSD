import pychrome
import time
import os
import glob
import pyautogui
import random
import pyperclip
import win32com.client
from bs4 import BeautifulSoup
# === ВКЛ/ВЫКЛ основных функций ===
DO_GOOGLE_AND_FIVERR = True
DO_AUTH = True
DO_PROFILE_SETUP = False
DO_GO_TO_CATEGORY = True  # <-- переход в новую категорию
DO_FIND_NEW_MEMBERS = True  # <--  функция парса
DO_OPEN_ALL_NEW_MEMBERS = True #<-сохранение новых мембов в файл

# === Настройки путей ===
script_dir = os.path.dirname(os.path.abspath(__file__))
accounts_path = os.path.join(script_dir, "accounts.txt")
photo_dir = r'C:\Users\userr\Desktop\PPlearn\Photos'  # <-- Укажи свою папку с фото!
used_photos_file = os.path.join(script_dir, "used_photos.txt")
script_dir = os.path.dirname(os.path.abspath(__file__))
new_members_file = r'C:\Users\userr\Desktop\PPlearn\NewMembers.txt'

# === Получаем логин и пароль ===
with open(accounts_path, "r", encoding="utf-8") as f:
    first_line = f.readline().strip()
login, password = first_line.split(":", 1)

# === Получаем уникальную фотографию ===
all_photos = sorted(
    glob.glob(os.path.join(photo_dir, "*.png")) +
    glob.glob(os.path.join(photo_dir, "*.jpg")) +
    glob.glob(os.path.join(photo_dir, "*.jpeg"))
)
if os.path.exists(used_photos_file):
    with open(used_photos_file, "r", encoding="utf-8") as f:
        used = set(line.strip() for line in f)
else:
    used = set()
photo_for_profile = None
for photo in all_photos:
    if photo not in used:
        photo_for_profile = photo
        break
if not photo_for_profile:
    raise Exception("Нет неиспользованных фото!")

print(f'Путь к файлу для загрузки: {photo_for_profile}')  # Для отладки!

browser = pychrome.Browser(url="http://127.0.0.1:9222")
tab = browser.list_tab()[0]
tab.start()
tab.call_method("Page.bringToFront")

def google_and_fiverr(tab):
    # 1. Открываем Google
    tab.call_method("Page.navigate", url="https://www.google.com")
    time.sleep(3)

    # 2. Фокусируем строку поиска через JS
    tab.call_method("Runtime.evaluate", expression='document.querySelector("input[name=\'q\']").focus();')
    time.sleep(1)

    # 3. Печатаем "fiverr"
    for ch in "fiverr":
        tab.call_method("Input.dispatchKeyEvent", type="keyDown", text=ch, unmodifiedText=ch, key=ch)
        tab.call_method("Input.dispatchKeyEvent", type="keyUp", text=ch, unmodifiedText=ch, key=ch)
        time.sleep(0.25)

    # 4. Enter для поиска
    tab.call_method("Input.dispatchKeyEvent", type="keyDown", windowsVirtualKeyCode=13, nativeVirtualKeyCode=13, key="Enter", code="Enter")
    tab.call_method("Input.dispatchKeyEvent", type="keyUp", windowsVirtualKeyCode=13, nativeVirtualKeyCode=13, key="Enter", code="Enter")
    time.sleep(3)

    # 5. Кликаем по первому результату поиска "Fiverr"
    tab.call_method(
        "Runtime.evaluate",
        expression="""
            var el = document.querySelector('h3.LC20lb.MBeuO.DKV0Md');
            if (el) el.closest('a').click();
        """
    )
    time.sleep(5)

def do_auth(tab, login, password):
    # 6. Кликаем по кнопке "Sign In" на Fiverr
    tab.call_method(
        "Runtime.evaluate",
        expression="""
            var signIn = document.querySelector('a[href^="/login?source=top_nav"]');
            if(signIn) { signIn.click(); }
        """
    )
    time.sleep(5)

    # 7. Кликаем по кнопке "Continue with email/username"
    tab.call_method(
        "Runtime.evaluate",
        expression="""
            var btns = document.querySelectorAll('button,div[role="button"],p');
            for (let btn of btns) {
                if (
                    btn.textContent &&
                    btn.textContent.trim().replace(/\\s+/g,' ') == "Continue with email/username"
                ) {
                    if (btn.parentElement.tagName.toLowerCase() == "button") {
                        btn.parentElement.click();
                    } else {
                        btn.click();
                    }
                    break;
                }
            }
        """
    )
    time.sleep(3)

    # 8. Фокус на поле логина
    tab.call_method(
        "Runtime.evaluate",
        expression='document.querySelector(\'input[name="email"]\').focus();'
    )
    time.sleep(1)

    # 9. Ввод логина с клавиатуры
    for ch in login:
        tab.call_method("Input.dispatchKeyEvent", type="keyDown", text=ch, unmodifiedText=ch, key=ch)
        tab.call_method("Input.dispatchKeyEvent", type="keyUp", text=ch, unmodifiedText=ch, key=ch)
        time.sleep(0.1)
    time.sleep(0.5)

    # 10. Переход на поле пароля (Tab)
    tab.call_method("Input.dispatchKeyEvent", type="keyDown", windowsVirtualKeyCode=9, nativeVirtualKeyCode=9, key="Tab", code="Tab")
    tab.call_method("Input.dispatchKeyEvent", type="keyUp", windowsVirtualKeyCode=9, nativeVirtualKeyCode=9, key="Tab", code="Tab")
    time.sleep(0.5)

    # 11. Ввод пароля с клавиатуры
    for ch in password:
        tab.call_method("Input.dispatchKeyEvent", type="keyDown", text=ch, unmodifiedText=ch, key=ch)
        tab.call_method("Input.dispatchKeyEvent", type="keyUp", text=ch, unmodifiedText=ch, key=ch)
        time.sleep(0.1)
    time.sleep(0.5)

    # 12. Кликаем по кнопке "Sign In"
    tab.call_method(
        "Runtime.evaluate",
        expression="""
            var btns = document.querySelectorAll('button');
            for (let btn of btns) {
                if (
                    btn.textContent &&
                    btn.textContent.trim().toLowerCase() === "sign in"
                ) {
                    btn.focus();
                    btn.click();
                    break;
                }
            }
        """
    )
    time.sleep(5)

def profile_setup(tab, photo_for_profile, used_photos_file):
    # 13. Кликаем по иконке профиля
    tab.call_method(
        "Runtime.evaluate",
        expression="""
            var btns = document.querySelectorAll('button.nav-popover-items-toggler');
            for (let btn of btns) {
                if (btn.style.borderRadius === "50%" || btn.innerText.length === 1) {
                    btn.click();
                    break;
                }
            }
        """
    )
    time.sleep(2)

    # 14. Кликаем по пункту "Profile"
    tab.call_method(
        "Runtime.evaluate",
        expression="""
            var menuLinks = document.querySelectorAll('a.nav-link');
            for (let link of menuLinks) {
                if (link.textContent.trim() === "Profile") {
                    link.click();
                    break;
                }
            }
        """
    )
    time.sleep(2)

    # 15. Кликаем по ссылке "here"
    tab.call_method(
        "Runtime.evaluate",
        expression="""
            var links = document.querySelectorAll('a');
            for (let link of links) {
                if (link.textContent.trim() === "here") {
                    link.click();
                    break;
                }
            }
        """
    )
    time.sleep(2)

    # === Клик мышкой по аватарке ===
    avatar_x, avatar_y = 320, 200  # ПОДГОНИ координаты под своё расположение окна!
    pyautogui.moveTo(avatar_x, avatar_y, duration=0.2)
    pyautogui.click()
    time.sleep(2.5)  # Ждём открытия проводника

    # === Вставка пути к фото и Enter ===
    pyautogui.write(photo_for_profile)
    time.sleep(0.5)
    pyautogui.press('enter')

    # === Помечаем фото как использованное ===
    with open(used_photos_file, "a", encoding="utf-8") as f:
        f.write(photo_for_profile + "\n")

    # === Клик мышкой по иконке карандаша (редактировать профиль) ===
    edit_pencil_x, edit_pencil_y = 415, 239  # координаты по скрину
    pyautogui.moveTo(edit_pencil_x, edit_pencil_y, duration=0.2)
    pyautogui.click()
    time.sleep(2)  # Ждём появления окна для редактирования имени

    # === Клик мышкой по полю ввода имени ===
    name_input_x, name_input_y = 1488, 420
    pyautogui.moveTo(name_input_x, name_input_y, duration=0.2)
    pyautogui.click()
    time.sleep(0.8)

    shell = win32com.client.Dispatch("WScript.Shell")
    time.sleep(3)
    shell.SendKeys("^a")  # Ctrl+A
    shell.SendKeys("{BACKSPACE}")  # Удалить текст
    for char in "Lilly":
        shell.SendKeys(char)
        time.sleep(0.4)
    shell.SendKeys("{ENTER}")
    time.sleep(1)  # Небольшая пауза для применения изменений

    # === Клик мышкой по координатам (1700, 750) ===
    intermediate_x, intermediate_y = 1700, 750  # Убедитесь, что координаты верные
    pyautogui.moveTo(intermediate_x, intermediate_y, duration=0.2)  # Перемещаем курсор
    pyautogui.click()  # Кликаем
    time.sleep(0.5)  # Небольшая пауза после клика

    # === Клик мышкой по кнопке "Save" ===
    save_button_x, save_button_y = 1850, 993  # Убедитесь, что координаты верные
    pyautogui.moveTo(save_button_x, save_button_y, duration=0.2)  # Перемещаем курсор к кнопке
    pyautogui.click()  # Кликаем по кнопке
    time.sleep(0.5)  # Небольшая пауза после клика

def go_to_category(tab):
    # 1. Переход на нужную категорию
    import time
    import os
    target_month_year = "Jun 2025"
    url = "https://www.fiverr.com/categories/music-audio/singers-vocalists?source=category_tree"
    tab.call_method("Page.navigate", url=url)
    time.sleep(5)
    # 2. Клик по "Seller details"
    tab.call_method(
        "Runtime.evaluate",
        expression="""
            var btns = document.querySelectorAll('button');
            for (let btn of btns) {
                if (
                    btn.offsetParent !== null &&
                    btn.textContent &&
                    btn.textContent.trim().toLowerCase() === "seller details"
                ) {
                    btn.click();
                    break;
                }
            }
        """
    )
    time.sleep(2)

    # 3. Ставим галочку "New Seller"
    tab.call_method(
        "Runtime.evaluate",
        expression="""
            var labels = document.querySelectorAll('label');
            for (let label of labels) {
                let input = label.querySelector('input[type="checkbox"][value="na"]');
                if (
                    input &&
                    label.textContent &&
                    label.textContent.trim().toLowerCase().includes("new seller") &&
                    !input.checked
                ) {
                    label.click();
                    break;
                }
            }
        """
    )
    time.sleep(1)

    # 4. Клик по кнопке "Apply"
    tab.call_method(
        "Runtime.evaluate",
        expression="""
            var btns = document.querySelectorAll('button');
            for (let btn of btns) {
                if (
                    btn.offsetParent !== null &&
                    btn.textContent &&
                    btn.textContent.trim().toLowerCase() === "apply"
                ) {
                    btn.click();
                    break;
                }
            }
        """
    )
    time.sleep(2)
      # 5. Клик по кнопке сортировки (Best selling)
    tab.call_method(
        "Runtime.evaluate",
        expression="""
            // Ищем кнопку сортировки по role="button" и содержимому текста
            var sortButtons = document.querySelectorAll('button[role="button"]');
            var clicked = false;
            
            for (let btn of sortButtons) {
                // Проверяем что кнопка видима и содержит текст сортировки
                if (
                    btn.offsetParent !== null && 
                    btn.textContent &&
                    (
                        btn.textContent.includes("Best selling") ||
                        btn.textContent.includes("Sort by") ||
                        btn.querySelector('span[class*="pre-title"]')
                    )
                ) {
                    console.log("Найдена кнопка сортировки:", btn.textContent);
                    btn.click();
                    clicked = true;
                    break;
                }
            }
            
            // Если не нашли по role="button", пробуем по классам
            if (!clicked) {
                var divButtons = document.querySelectorAll('div[role="button"]');
                for (let btn of divButtons) {
                    if (
                        btn.offsetParent !== null && 
                        btn.textContent &&
                        btn.textContent.includes("Best selling")
                    ) {
                        console.log("Найдена div кнопка сортировки:", btn.textContent);
                        btn.click();
                        clicked = true;
                        break;
                    }
                }
            }
            
            clicked; // возвращаем результат
        """
    )
    time.sleep(2)

# 6. Клик по "Newest arrivals" в выпадающем меню
    tab.call_method(
        "Runtime.evaluate",
        expression="""
            // Ищем label с текстом "Newest arrivals"
            var labels = document.querySelectorAll('label');
            var clicked = false;
            
            for (let label of labels) {
                if (
                    label.offsetParent !== null &&
                    label.textContent &&
                    label.textContent.trim() === "Newest arrivals"
                ) {
                    console.log("Найден label с Newest arrivals");
                    label.click();
                    clicked = true;
                    break;
                }
            }
            
            // Если не сработало через label, пробуем через родительский div
            if (!clicked) {
                var divs = document.querySelectorAll('div[class*="label-item"]');
                for (let div of divs) {
                    if (
                        div.offsetParent !== null &&
                        div.textContent &&
                        div.textContent.includes("Newest arrivals")
                    ) {
                        console.log("Найден div с Newest arrivals");
                        div.click();
                        clicked = true;
                        break;
                    }
                }
            }
            
            // Последняя попытка - поиск по всем элементам с классом vp91gtk
            if (!clicked) {
                var elements = document.querySelectorAll('[class*="vp91gtk"]');
                for (let el of elements) {
                    if (
                        el.offsetParent !== null &&
                        el.textContent &&
                        el.textContent.trim() === "Newest arrivals"
                    ) {
                        console.log("Найден элемент с классом vp91gtk");
                        el.click();
                        break;
                    }
                }
            }
            
            clicked; // возвращаем результат
        """
    )
    time.sleep(2)
    

    """
    Поиск 7 участников зарегистрированных в June 2025
    Алгоритм:
    1. Клик по объявлению
    2. Поиск даты "Jun 2025" 
    3. Сохранение ссылки если дата подходит
    4. Возврат назад и переход к следующему
    5. Повторяем до 7 найденных участников
    """
    print("Начинаем поиск новых участников June 2025...")
    
    found_members = 0
    target_members = 7
    current_listing = 1
    
    # Читаем уже найденных участников (если файл существует)
    existing_links = set()
    if os.path.exists(new_members_file):
        with open(new_members_file, "r", encoding="utf-8") as f:
            existing_links = set(line.strip() for line in f if line.strip())
            found_members = len(existing_links)
    
    print(f"Уже найдено участников: {found_members}")
    
    while found_members < target_members:
        print(f"Проверяем объявление #{current_listing}...")
        
        # 1. Клик по текущему объявлению
        listing_clicked = tab.call_method(
            "Runtime.evaluate",
            expression=f"""
                // Ищем карточки объявлений по разным селекторам
                var listings = document.querySelectorAll('article a, div[data-impression-collected] a, .gig-card-layout a, a[href*="/gigs/"]');
                
                // Фильтруем только ссылки которые ведут на гиги
                var gigLinks = [];
                for (let link of listings) {{
                    if (link.href && link.href.includes('/gigs/') && link.offsetParent !== null) {{
                        gigLinks.push(link);
                    }}
                }}
                
                console.log("Найдено объявлений:", gigLinks.length);
                
                if (gigLinks.length >= {current_listing}) {{
                    var listing = gigLinks[{current_listing - 1}];
                    console.log("Кликаем по объявлению #{current_listing}:", listing.href);
                    
                    // Скроллим к элементу перед кликом
                    listing.scrollIntoView({{behavior: 'smooth', block: 'center'}});
                    
                    setTimeout(function() {{
                        listing.click();
                    }}, 1000);
                    
                    true;
                }} else {{
                    console.log("Не найдено объявление #{current_listing}, всего найдено:", gigLinks.length);
                    false;
                }}
            """
        )
        
        if not listing_clicked.get('result', {}).get('value'):
            print("Объявления закончились, выходим...")
            break
            
        time.sleep(3)  # Ждем загрузки страницы объявления
        
        # 2. Поиск даты регистрации "Jun 2025"
        date_check = tab.call_method(
            "Runtime.evaluate",
            expression="""
                var found = false;
                var currentUrl = window.location.href;
                
                // Ищем все элементы содержащие "Jun 2025"
                var allElements = document.querySelectorAll('*');
                for (let el of allElements) {
                    if (el.textContent && el.textContent.includes('Jun 2025')) {
                        console.log("Найдена дата Jun 2025:", el.textContent);
                        found = true;
                        break;
                    }
                }
                
                {found: found, url: currentUrl};
            """
        )
        
        result = date_check.get('result', {}).get('value', {})
        current_url = result.get('url', '')
        is_june_2025 = result.get('found', False)
        
        # 3. Сохраняем ссылку если дата подходит
        if is_june_2025 and current_url not in existing_links:
            with open(new_members_file, "a", encoding="utf-8") as f:
                f.write(current_url + "\n")
            existing_links.add(current_url)
            found_members += 1
            print(f"✓ Сохранен участник #{found_members}: {current_url}")
        else:
            print("✗ Участник не подходит или уже сохранен")
        
        # 4. Возврат на прошлую страницу
        tab.call_method("Page.goBack")
        time.sleep(2)  # Ждем загрузки страницы категории
        
        current_listing += 1
        
        # Проверяем не нужно ли перейти на следующую страницу
        if current_listing > 20:  # Примерно 20 объявлений на странице
            print("Переходим на следующую страницу...")
            next_page_clicked = tab.call_method(
                "Runtime.evaluate",
                expression="""
                    var nextBtn = document.querySelector('a[aria-label="Next"]') || 
                                  document.querySelector('button[aria-label="Next"]') ||
                                  document.querySelector('a:contains("Next")');
                    if (nextBtn) {
                        nextBtn.click();
                        true;
                    } else {
                        false;
                    }
                """
            )
            
            if next_page_clicked.get('result', {}).get('value'):
                time.sleep(3)
                current_listing = 1
            else:
                print("Следующая страница не найдена, заканчиваем поиск...")
                break
    
    print(f"Поиск завершен! Найдено участников: {found_members}/{target_members}")


    """
    Поиск 7 участников зарегистрированных в June 2025
    """
    print("Начинаем поиск новых участников June 2025...")
    
    found_members = 0
    target_members = 7
    current_listing = 1
    
    # Читаем уже найденных участников
    existing_links = set()
    if os.path.exists(new_members_file):
        with open(new_members_file, "r", encoding="utf-8") as f:
            existing_links = set(line.strip() for line in f if line.strip())
            found_members = len(existing_links)
    
    print(f"Уже найдено участников: {found_members}")
    
    # Сначала проверим что вообще есть на странице
    print("Анализируем структуру страницы...")
    page_analysis = tab.call_method(
        "Runtime.evaluate",
        expression="""
            // Ждем немного для полной загрузки
            setTimeout(function() {
                var allLinks = document.querySelectorAll('a[href*="/gigs/"]');
                var gigCardLayouts = document.querySelectorAll('.gig-card-layout');
                var dataImpressions = document.querySelectorAll('[data-impression-item]');
                var articles = document.querySelectorAll('article');
                
                console.log("Найдено ссылок с /gigs/:", allLinks.length);
                console.log("Найдено .gig-card-layout:", gigCardLayouts.length);
                console.log("Найдено [data-impression-item]:", dataImpressions.length);
                console.log("Найдено articles:", articles.length);
                
                // Попробуем найти любые элементы которые могут быть карточками
                var possibleCards = document.querySelectorAll('div[class*="gig"], div[class*="card"], div[data-gig-id], article[data-gig-id]');
                console.log("Найдено возможных карточек:", possibleCards.length);
                
                return {
                    gigLinks: allLinks.length,
                    gigCards: gigCardLayouts.length,
                    dataImpressions: dataImpressions.length,
                    articles: articles.length,
                    possibleCards: possibleCards.length,
                    url: window.location.href
                };
            }, 2000);
        """
    )
    
    time.sleep(3)  # Ждем выполнения анализа
    
    while found_members < target_members:
        print(f"Проверяем объявление #{current_listing}...")
        
        # Скроллим немного вниз
        tab.call_method("Runtime.evaluate", expression="window.scrollBy(0, 500);")
        time.sleep(2)
        
        # Пробуем разные способы найти и кликнуть по объявлениям
        click_result = tab.call_method(
            "Runtime.evaluate",
            expression=f"""
                var clicked = false;
                var foundUrl = null;
                var method = 'none';
                
                // Способ 1: Прямые ссылки на гиги
                var gigLinks = document.querySelectorAll('a[href*="/gigs/"]');
                if (gigLinks.length >= {current_listing} && !clicked) {{
                    var link = gigLinks[{current_listing - 1}];
                    if (link && link.offsetParent !== null) {{
                        foundUrl = link.href;
                        method = 'direct_gig_link';
                        link.scrollIntoView({{behavior: 'smooth', block: 'center'}});
                        setTimeout(function() {{ link.click(); }}, 500);
                        clicked = true;
                    }}
                }}
                
                // Способ 2: Карточки с классом gig-card-layout
                if (!clicked) {{
                    var gigCards = document.querySelectorAll('.gig-card-layout');
                    if (gigCards.length >= {current_listing}) {{
                        var card = gigCards[{current_listing - 1}];
                        var link = card.querySelector('a');
                        if (link && link.href) {{
                            foundUrl = link.href;
                            method = 'gig_card_layout';
                            card.scrollIntoView({{behavior: 'smooth', block: 'center'}});
                            setTimeout(function() {{ link.click(); }}, 500);
                            clicked = true;
                        }}
                    }}
                }}
                
                // Способ 3: Элементы с data-impression-item
                if (!clicked) {{
                    var impressionItems = document.querySelectorAll('[data-impression-item]');
                    if (impressionItems.length >= {current_listing}) {{
                        var item = impressionItems[{current_listing - 1}];
                        var link = item.querySelector('a[href*="/gigs/"]') || item.querySelector('a');
                        if (link && link.href && link.href.includes('/gigs/')) {{
                            foundUrl = link.href;
                            method = 'impression_item';
                            item.scrollIntoView({{behavior: 'smooth', block: 'center'}});
                            setTimeout(function() {{ link.click(); }}, 500);
                            clicked = true;
                        }}
                    }}
                }}
                
                // Способ 4: Articles
                if (!clicked) {{
                    var articles = document.querySelectorAll('article');
                    if (articles.length >= {current_listing}) {{
                        var article = articles[{current_listing - 1}];
                        var link = article.querySelector('a[href*="/gigs/"]') || article.querySelector('a');
                        if (link && link.href) {{
                            foundUrl = link.href;
                            method = 'article';
                            article.scrollIntoView({{behavior: 'smooth', block: 'center'}});
                            setTimeout(function() {{ link.click(); }}, 500);
                            clicked = true;
                        }}
                    }}
                }}
                
                console.log('Метод поиска:', method);
                console.log('Найденная ссылка:', foundUrl);
                console.log('Клик выполнен:', clicked);
                
                return {{
                    clicked: clicked,
                    url: foundUrl,
                    method: method,
                    totalGigLinks: document.querySelectorAll('a[href*="/gigs/"]').length,
                    totalCards: document.querySelectorAll('.gig-card-layout').length,
                    totalImpressions: document.querySelectorAll('[data-impression-item]').length,
                    totalArticles: document.querySelectorAll('article').length
                }};
            """
        )
        
        result = click_result.get('result', {}).get('value', {})
        
        print(f"Результат поиска:")
        print(f"  Найдено gig ссылок: {result.get('totalGigLinks', 0)}")
        print(f"  Найдено карточек: {result.get('totalCards', 0)}")
        print(f"  Найдено impression items: {result.get('totalImpressions', 0)}")
        print(f"  Найдено articles: {result.get('totalArticles', 0)}")
        print(f"  Использованный метод: {result.get('method', 'none')}")
        print(f"  URL: {result.get('url', 'none')}")
        
        if not result.get('clicked'):
            print("Не удалось найти или кликнуть по объявлению")
            
            # Попробуем перейти на следующую страницу
            print("Ищем кнопку следующей страницы...")
            next_page = tab.call_method(
                "Runtime.evaluate",
                expression="""
                    var nextButtons = [
                        document.querySelector('a[aria-label="Next"]'),
                        document.querySelector('button[aria-label="Next"]'),
                        document.querySelector('a[title="Next"]'),
                        document.querySelector('.pagination a:last-child'),
                        document.querySelector('a:contains("Next")'),
                        document.querySelector('button:contains("Next")')
                    ];
                    
                    for (let btn of nextButtons) {
                        if (btn && !btn.disabled && btn.offsetParent !== null) {
                            console.log('Найдена кнопка Next, кликаем...');
                            btn.click();
                            return {found: true, text: btn.textContent || btn.getAttribute('aria-label')};
                        }
                    }
                    
                    return {found: false, text: null};
                """
            )
            
            if next_page.get('result', {}).get('value', {}).get('found'):
                print("Переходим на следующую страницу...")
                time.sleep(5)
                current_listing = 1
                continue
            else:
                print("Кнопка 'Next' не найдена, заканчиваем поиск")
                break
        
        # Ждем загрузки страницы объявления
        time.sleep(4)
        
        # Проверяем что перешли на страницу объявления
        page_check = tab.call_method(
            "Runtime.evaluate",
            expression="""
                var url = window.location.href;
                var isGigPage = url.includes('/gigs/');
                return {url: url, isGigPage: isGigPage};
            """
        )
        
        page_result = page_check.get('result', {}).get('value', {})
        current_url = page_result.get('url', '')
        
        if not page_result.get('isGigPage'):
            print(f"Не перешли на страницу объявления. Текущий URL: {current_url}")
            current_listing += 1
            continue
        
        print(f"✓ Перешли на страницу объявления: {current_url}")
        
        # Ищем дату регистрации June 2025
        date_search = tab.call_method(
            "Runtime.evaluate",
            expression="""
                var found = false;
                var foundText = '';
                
                // Ждем немного для загрузки контента
                setTimeout(function() {
                    var allText = document.body.textContent || document.body.innerText || '';
                    
                    // Ищем различные варианты June 2025
                    var patterns = [
                        'Jun 2025', 'June 2025', 'jun 2025', 'june 2025',
                        'Joined in Jun 2025', 'Member since Jun 2025',
                        'Joined Jun 2025', 'Since Jun 2025'
                    ];
                    
                    for (let pattern of patterns) {
                        if (allText.includes(pattern)) {
                            found = true;
                            foundText = pattern;
                            console.log('Найдена дата:', pattern);
                            break;
                        }
                    }
                    
                    // Дополнительный поиск в элементах
                    if (!found) {
                        var elements = document.querySelectorAll('*');
                        for (let el of elements) {
                            if (el.textContent && el.offsetParent !== null) {
                                var text = el.textContent.trim();
                                if (text.includes('Jun 2025') || text.includes('June 2025')) {
                                    found = true;
                                    foundText = text;
                                    console.log('Найдена дата в элементе:', text);
                                    break;
                                }
                            }
                        }
                    }
                }, 1000);
                
                return {found: found, text: foundText};
            """
        )
        
        time.sleep(2)  # Ждем выполнения поиска даты
        
        date_result = date_search.get('result', {}).get('value', {})
        is_june_2025 = date_result.get('found', False)
        
        if is_june_2025 and current_url not in existing_links:
            with open(new_members_file, "a", encoding="utf-8") as f:
                f.write(current_url + "\n")
            existing_links.add(current_url)
            found_members += 1
            print(f"✓ Найден участник #{found_members}: {current_url}")
            print(f"  Дата: {date_result.get('text', '')}")
        else:
            if current_url in existing_links:
                print("✗ Участник уже был сохранен")
            else:
                print("✗ Участник не из June 2025")
        
        # Возвращаемся назад
        print("Возвращаемся на страницу категории...")
        tab.call_method("Page.goBack")
        time.sleep(3)
        
        current_listing += 1
        
        # Если проверили много объявлений, переходим на следующую страницу
        if current_listing > 15:
            print("Переходим на следующую страницу...")
            next_page = tab.call_method(
                "Runtime.evaluate",
                expression="""
                    var nextBtn = document.querySelector('a[aria-label="Next"]') || 
                                  document.querySelector('button[aria-label="Next"]');
                    if (nextBtn && !nextBtn.disabled) {
                        nextBtn.click();
                        return true;
                    }
                    return false;
                """
            )
            
            if next_page.get('result', {}).get('value'):
                time.sleep(4)
                current_listing = 1
            else:
                print("Больше страниц нет")
                break
    
    print(f"Поиск завершен! Найдено участников: {found_members}/{target_members}")


    """
    Парсит до 20 ссылок на объявления из исходного HTML-кода страницы (ищет <a ... aria-label="Go to gig" ... href="...pos=...">)
    и сохраняет их в new_members_file с удобной нумерацией.
    """
    print("Сохраняем исходный HTML страницы...")

    # Получаем весь HTML страницы
    html_result = tab.call_method("Runtime.evaluate", expression="document.documentElement.outerHTML")
    html = html_result.get("result", {}).get("value", "")

    # Парсим HTML
    soup = BeautifulSoup(html, 'html.parser')
    links = []
    for a in soup.find_all('a', href=True, attrs={'aria-label': 'Go to gig'}):
        href = a['href']
        if 'pos=' in href:
            # Преобразуем относительную ссылку в абсолютную
            if href.startswith('/'):
                href = "https://www.fiverr.com" + href
            if href not in links:
                links.append(href)
        if len(links) >= 20:
            break

    print(f"Найдено ссылок: {len(links)}")
    if links:
        with open(new_members_file, "w", encoding="utf-8") as f:
            for idx, url in enumerate(links, 1):
                f.write(f"{idx}. {url}\n")
        print(f"Ссылки успешно сохранены в {new_members_file} с нумерацией")
    else:
        print("Ссылки на объявления не найдены.")


    """
    Открывает первую ссылку из файла new_members_file в браузере (игнорируя нумерацию),
    затем находит и выводит дату регистрации пользователя ("Member since ...").
    """
    import os
    import time

    print(f"Читаем файл ссылок: {new_members_file}")
    if not os.path.exists(new_members_file):
        print("Файл ссылок не найден!")
        return

    url = None
    with open(new_members_file, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            # Убираем возможную нумерацию ("1. " или "01. ")
            parts = line.split(". ", 1)
            url = parts[1] if len(parts) > 1 else parts[0]
            # Проверяем, что это действительно ссылка
            if url.startswith("http"):
                print(f"Открываем первую ссылку: {url}")
                tab.call_method("Page.navigate", url=url)
                time.sleep(5)  # Можно увеличить, если страница грузится долго
                break

    if not url:
        print("В файле не найдено подходящих ссылок.")
        return

    # === Поиск и вывод даты регистрации пользователя ===
    # Ждем полной загрузки страницы
    time.sleep(2)
    result = tab.call_method(
        "Runtime.evaluate",
        expression="""
            var lis = document.querySelectorAll("ul.user-stats li");
            for (var i = 0; i < lis.length; i++) {
                if (lis[i].textContent.includes("Member since")) {
                    var strong = lis[i].querySelector("strong");
                    if (strong) {
                        return strong.textContent.trim();
                    }
                }
            }
            return null;
        """
    )
    reg_date = result.get("result", {}).get("value", None)
    if reg_date:
        print(f"Дата регистрации пользователя: {reg_date}")
    else:
        print("Дата регистрации не найдена.")


    save_path = r"C:\Users\userr\Desktop\PPlearn\ParsedMembers.txt"
    print(f"Читаем файл ссылок: {new_members_file}")
    if not os.path.exists(new_members_file):
        print("Файл ссылок не найден!")
        return

    urls = []
    with open(new_members_file, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            parts = line.split(". ", 1)
            url = parts[1] if len(parts) > 1 else parts[0]
            if url.startswith("http"):
                urls.append(url)
    if not urls:
        print("В файле не найдено подходящих ссылок.")
        return

    # Читаем уже сохранённые ссылки, чтобы продолжать нумерацию (если файл уже существует)
    parsed_links = []
    if os.path.exists(save_path):
        with open(save_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    parsed_links.append(line)

    match_count = len(parsed_links)

    for idx, url in enumerate(urls[:20], 1):
        print(f"\n[{idx}] Открываем ссылку: {url}")
        tab.call_method("Page.navigate", url=url)
        time.sleep(5)  # Ждем загрузки страницы

        # Основной способ поиска даты регистрации через user-stats
        time.sleep(2)
        result = tab.call_method(
            "Runtime.evaluate",
            expression="""
                var lis = document.querySelectorAll("ul.user-stats li");
                for (var i = 0; i < lis.length; i++) {
                    if (lis[i].textContent.includes("Member since")) {
                        var strong = lis[i].querySelector("strong");
                        if (strong) {
                            return strong.textContent.trim();
                        }
                    }
                }
                return null;
            """
        )
        reg_date = result.get("result", {}).get("value", None)

        # Альтернативный способ: поиск по всему HTML, если reg_date не найден
        if not reg_date:
            html_result = tab.call_method("Runtime.evaluate", expression="document.documentElement.outerHTML")
            html = html_result.get("result", {}).get("value", "")
            soup = BeautifulSoup(html, "html.parser")
            found = False
            for li in soup.find_all("li"):
                if "Member since" in li.text:
                    strong = li.find("strong")
                    if strong and strong.text.strip():
                        reg_date = strong.text.strip()
                        found = True
                        break
            if not found:
                import re
                patterns = [
                    r"[JFMASOND][a-z]+\s20\d\d",
                    r"Member since\s*:? ?([A-Za-z]+\s20\d\d)",
                ]
                match = soup.find(string=re.compile(r"Member since\s*:? ?([A-Za-z]+\s20\d\d)"))
                if match:
                    m = re.search(r"Member since\s*:? ?([A-Za-z]+\s20\d\d)", match)
                    if m:
                        reg_date = m.group(1)
                        found = True
                if not found:
                    for pattern in patterns:
                        m = re.search(pattern, html)
                        if m:
                            reg_date = m.group(0)
                            found = True
                            break

        if reg_date:
            print(f"[{idx}] Дата регистрации пользователя: {reg_date}")
            if reg_date == target_month_year:
                match_count += 1
                with open(save_path, "a", encoding="utf-8") as out:
                    out.write(f"{match_count}. {url}\n")
                print(f"[{idx}] Совпадение найдено! Ссылка сохранена в ParsedMembers.txt")
        else:
            print(f"[{idx}] Дата регистрации не найдена ни одним методом.")

def open_all_new_members(tab, new_members_file, target_month_year="Jun 2025"):
    """
    Открывает до 20 ссылок, ищет дату регистрации пользователя,
    если дата совпадает с target_month_year — сохраняет ссылку в ParsedMembers.txt с нумерацией.
    """
    from bs4 import BeautifulSoup

    save_path = r"C:\Users\userr\Desktop\PPlearn\ParsedMembers.txt"
    print(f"Читаем файл ссылок: {new_members_file}")
    if not os.path.exists(new_members_file):
        print("Файл ссылок не найден!")
        return

    urls = []
    with open(new_members_file, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            parts = line.split(". ", 1)
            url = parts[1] if len(parts) > 1 else parts[0]
            if url.startswith("http"):
                urls.append(url)
    if not urls:
        print("В файле не найдено подходящих ссылок.")
        return

    # Читаем уже сохранённые ссылки для продолжения нумерации
    match_count = 0
    if os.path.exists(save_path):
        with open(save_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and ". " in line:
                    try:
                        num = int(line.split(". ", 1)[0])
                        match_count = max(match_count, num)
                    except Exception:
                        pass

    for idx, url in enumerate(urls[:20], 1):
        print(f"\n[{idx}] Открываем ссылку: {url}")
        tab.call_method("Page.navigate", url=url)
        time.sleep(5)

        # Основной способ поиска даты регистрации через user-stats
        time.sleep(2)
        result = tab.call_method(
            "Runtime.evaluate",
            expression="""
                var lis = document.querySelectorAll("ul.user-stats li");
                for (var i = 0; i < lis.length; i++) {
                    if (lis[i].textContent.includes("Member since")) {
                        var strong = lis[i].querySelector("strong");
                        if (strong) {
                            return strong.textContent.trim();
                        }
                    }
                }
                return null;
            """
        )
        reg_date = result.get("result", {}).get("value", None)

        # Альтернативный способ: поиск по всему HTML, если reg_date не найден
        if not reg_date:
            html_result = tab.call_method("Runtime.evaluate", expression="document.documentElement.outerHTML")
            html = html_result.get("result", {}).get("value", "")
            soup = BeautifulSoup(html, "html.parser")
            found = False
            for li in soup.find_all("li"):
                if "Member since" in li.text:
                    strong = li.find("strong")
                    if strong and strong.text.strip():
                        reg_date = strong.text.strip()
                        found = True
                        break
            if not found:
                import re
                patterns = [
                    r"[JFMASOND][a-z]+\s20\d\d",
                    r"Member since\s*:? ?([A-Za-z]+\s20\d\d)",
                ]
                match = soup.find(string=re.compile(r"Member since\s*:? ?([A-Za-z]+\s20\d\d)"))
                if match:
                    m = re.search(r"Member since\s*:? ?([A-Za-z]+\s20\d\d)", match)
                    if m:
                        reg_date = m.group(1)
                        found = True
                if not found:
                    for pattern in patterns:
                        m = re.search(pattern, html)
                        if m:
                            reg_date = m.group(0)
                            found = True
                            break

        print(f"[{idx}] Дата регистрации пользователя: {reg_date}")

        # --- Исправленное сравнение и сохранение ---
        if reg_date and reg_date.strip().lower() == target_month_year.strip().lower():
            match_count += 1
            with open(save_path, "a", encoding="utf-8") as out:
                out.write(f"{match_count}. {url}\n")
            print(f"[{idx}] Совпадение найдено! Ссылка сохранена в ParsedMembers.txt")
        else:
            print(f"[{idx}] Не совпадает с целевой датой ({target_month_year}) или не найдена.")

    print(f"\nОбработка завершена. Совпадений: {match_count}")
# === Основная логика ===
if DO_GOOGLE_AND_FIVERR:
    google_and_fiverr(tab)

if DO_AUTH:
    do_auth(tab, login, password)

if DO_PROFILE_SETUP:
    profile_setup(tab, photo_for_profile, used_photos_file)

if DO_GO_TO_CATEGORY:
    go_to_category(tab)

if DO_OPEN_ALL_NEW_MEMBERS:
    open_all_new_members(tab, new_members_file)
tab.stop()