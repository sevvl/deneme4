import requests
from bs4 import BeautifulSoup
import pandas as pd
import csv
import os
from datetime import datetime


def scrape_grape_disease_data(url, save_to_csv=True):
    """
    Üzüm hastalığı fungisit verilerini çeker

    Args:
        url (str): Çekilecek web sayfasının URL'i
        save_to_csv (bool): Veriyi CSV'ye kaydet

    Returns:
        list: Çekilen veri listesi veya None
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:98.0) Gecko/20100101 Firefox/98.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        "Cache-Control": "max-age=0",
    }

    try:
        print("🔄 Web sayfasından veri çekiliyor...")
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        # Tabloyu bul - farklı seçicileri dene
        table = None
        selectors = [
            {'class': 'tablestyle'},
            {'class': 'table'},
            {'id': 'fungicide-table'},
            None  # Herhangi bir tablo
        ]

        for selector in selectors:
            if selector:
                table = soup.find('table', selector)
            else:
                table = soup.find('table')

            if table:
                print(f"✅ Tablo bulundu: {selector}")
                break

        if table:
            data = []
            rows = table.find_all('tr')

            if not rows:
                print("❌ Tabloda satır bulunamadı.")
                return None

            # Header'ları çıkar
            header_row = rows[0]
            headers = []

            # Önce th etiketlerini dene
            th_elements = header_row.find_all('th')
            if th_elements:
                headers = [th.get_text(strip=True, separator=' ') for th in th_elements]
            else:
                # th yoksa td'lerden header çıkar
                td_elements = header_row.find_all('td')
                if td_elements:
                    headers = [td.get_text(strip=True, separator=' ') for td in td_elements]

            # Header'ları temizle
            headers = [h.replace('\n', ' ').replace('\r', ' ') for h in headers if h.strip()]

            if headers:
                data.append(headers)
                print(f"✅ {len(headers)} sütunlu header bulundu")

                # Veri satırlarını işle
                successful_rows = 0
                for row in rows[1:]:
                    cells = row.find_all(['td', 'th'])
                    if cells:
                        row_data = []
                        for cell in cells:
                            # Hücre içeriğini temizle
                            cell_text = cell.get_text(strip=True, separator=' ')
                            cell_text = cell_text.replace('\n', ' ').replace('\r', ' ')
                            row_data.append(cell_text)

                        # Boş olmayan satırları ekle
                        if any(cell.strip() for cell in row_data) and len(row_data) >= len(headers):
                            # Sütun sayısını eşitle
                            while len(row_data) < len(headers):
                                row_data.append('')
                            row_data = row_data[:len(headers)]  # Fazla sütunları kes

                            data.append(row_data)
                            successful_rows += 1

                print(f"✅ {successful_rows} veri satırı işlendi")

                # CSV'ye kaydet
                if save_to_csv and data:
                    try:
                        filename = 'grape_disease_data.csv'
                        with open(filename, 'w', newline='', encoding='utf-8') as f:
                            writer = csv.writer(f)
                            writer.writerows(data)
                        print(f"💾 Veri '{filename}' dosyasına kaydedildi")

                        # Metadata dosyası oluştur
                        metadata = {
                            'last_updated': datetime.now().isoformat(),
                            'source_url': url,
                            'total_rows': len(data),
                            'columns': len(headers) if headers else 0
                        }

                        with open('data_metadata.txt', 'w', encoding='utf-8') as f:
                            for key, value in metadata.items():
                                f.write(f"{key}: {value}\n")

                    except Exception as e:
                        print(f"❌ CSV kaydetme hatası: {e}")

                return data
            else:
                print("❌ Header bulunamadı")
                return None
        else:
            print("❌ Tablo bulunamadı")
            return None

    except requests.exceptions.Timeout:
        print("❌ Zaman aşımı - Web sitesi yavaş yanıt veriyor")
        return None
    except requests.exceptions.RequestException as e:
        print(f"❌ İstek hatası: {e}")
        return None
    except Exception as e:
        print(f"❌ Beklenmeyen hata: {e}")
        return None


def load_cached_data():
    """
    Daha önce kaydedilmiş CSV verilerini yükle
    """
    try:
        if os.path.exists('grape_disease_data.csv'):
            df = pd.read_csv('grape_disease_data.csv')

            # Metadata kontrolü
            if os.path.exists('data_metadata.txt'):
                with open('data_metadata.txt', 'r', encoding='utf-8') as f:
                    metadata = f.read()
                    print(f"📋 Cached veri bilgisi:\n{metadata}")

            return df
        else:
            print("❌ Önbellek dosyası bulunamadı")
            return None
    except Exception as e:
        print(f"❌ Önbellek yükleme hatası: {e}")
        return None
import requests
from bs4 import BeautifulSoup
import pandas as pd

def scrape_umass_fungicide_table():
    url = "https://www.umass.edu/agriculture-food-environment/fruit/ne-small-fruit-management-guide/grapes/diseases/table-54-effectiveness-of-fungicides-on-grape-diseases"

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Hata: Sayfa alınamadı. {e}")
        return None

    # 1. İlk olarak pandas ile tabloyu yakalamayı dene
    try:
        dfs = pd.read_html(response.text)
        for df in dfs:
            if 'Phomopsis Cane and Leaf Spot' in df.columns:
                print("✅ Tablo pandas.read_html ile başarıyla bulundu.")
                return df
    except Exception as e:
        print(f"❌ pandas.read_html ile tablo alınamadı: {e}")

    # 2. Eğer pandas ile olmadıysa, BeautifulSoup ile elle bul
    soup = BeautifulSoup(response.text, 'html.parser')
    table = None

    for t in soup.find_all('table'):
        caption = t.find('caption')
        if caption and 'Effectiveness of Fungicides' in caption.get_text():
            table = t
            print("✅ Tablo BeautifulSoup ile caption üzerinden bulundu.")
            break
        elif 'Effectiveness of Fungicides' in t.get_text()[:300]:
            table = t
            print("✅ Tablo BeautifulSoup ile metin taramasıyla bulundu.")
            break

    if table:
        try:
            df = pd.read_html(str(table))[0]
            return df
        except Exception as e:
            print(f"❌ Tablo pandas.read_html ile işlenemedi: {e}")
            return None

    print("❌ Tablo bulunamadı.")
    return None


# Bu fonksiyonu çağırarak sonucu yazdır
if __name__ == "__main__":
    df = scrape_umass_fungicide_table()
    if df is not None:
        print(df.head())
        df.to_csv("fungicide_effectiveness.csv", index=False)
        print("✅ Tablo 'fungicide_effectiveness.csv' olarak kaydedildi.")
    else:
        print("❌ Veri çekilemedi.")


def get_grape_data_smart(force_refresh=False):
    """
    Akıllı veri çekme - önce önbelleği kontrol et, gerekirse yenile
    """
    url = "https://www.umass.edu/agriculture-food-environment/fruit/ne-small-fruit-management-guide/grapes/diseases/table-54-effectiveness-of-fungicides-on-grape-diseases"

    if not force_refresh:
        # Önce önbellekteki veriyi dene
        cached_df = load_cached_data()
        if cached_df is not None and not cached_df.empty:
            print("✅ Önbellekten veri yüklendi")
            return cached_df

    # Önbellek yoksa veya yenileme isteniyorsa web'den çek
    print("🌐 Web'den yeni veri çekiliyor...")
    raw_data = scrape_grape_disease_data(url)

    if raw_data and len(raw_data) > 1:
        try:
            df = pd.DataFrame(raw_data[1:], columns=raw_data[0])
            return df
        except Exception as e:
            print(f"❌ DataFrame oluşturma hatası: {e}")
            return None
    else:
        return None


if __name__ == "__main__":
    print("🍇 Üzüm Hastalığı Veri Çekici")
    print("=" * 40)

    # Test çalıştırma
    df = get_grape_data_smart()

    if df is not None:
        print(f"\n📊 Başarı! {len(df)} satır, {len(df.columns)} sütun")
        print("Sütunlar:", list(df.columns))
        print("\nİlk 3 satır:")
        print(df.head(3).to_string())
    else:
        print("❌ Veri çekilemedi!")

    print("\n" + "=" * 40)
    print("Test tamamlandı!")