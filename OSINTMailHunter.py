import sys
import google.generativeai as genai
from urllib.parse import unquote
from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QTextEdit
from googlesearch import search

# Google AI API Anahtarı
GOOGLE_AI_API_KEY = "" # Keyinizi kendiniz giriniz

try:
    if GOOGLE_AI_API_KEY != "YOUR_GOOGLE_AI_API_KEY":
        genai.configure(api_key=GOOGLE_AI_API_KEY)
except Exception as e:
    print(f"API Anahtarı yapılandırılamadı. Hata: {e}")


class EmailFinderApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Gelişmiş Kurumsal E-posta Bulucu')
        self.setGeometry(100, 100, 500, 450)
        self.init_ui()
        self.model = None
        try:
            if GOOGLE_AI_API_KEY != "YOUR_GOOGLE_AI_API_KEY":
                self.model = genai.GenerativeModel('gemini-1.5-flash-latest')
        except Exception as e:
            print(f"Model yüklenemedi: {e}")

    def init_ui(self):
        # Arayüz kodu
        self.kurum_label = QLabel('Kurum Adı:')
        self.kurum_input = QLineEdit()
        self.kurum_input.setPlaceholderText('Microsoft')
        self.unvan_label = QLabel('Çalışan Unvanı:')
        self.unvan_input = QLineEdit()
        self.unvan_input.setPlaceholderText('Manager, Developer')
        self.domain_label = QLabel('Domain:')
        self.domain_input = QLineEdit()
        self.domain_input.setPlaceholderText('microsoft.com')
        self.ara_button = QPushButton('E-postaları Bul')
        self.sonuc_alanı = QTextEdit()
        self.sonuc_alanı.setReadOnly(True)
        self.ara_button.clicked.connect(self.baslat)
        layout = QVBoxLayout()
        layout.addWidget(self.kurum_label)
        layout.addWidget(self.kurum_input)
        layout.addWidget(self.unvan_label)
        layout.addWidget(self.unvan_input)
        layout.addWidget(self.domain_label)
        layout.addWidget(self.domain_input)
        layout.addWidget(self.ara_button)
        layout.addWidget(QLabel('Bulunan Olası E-postalar:'))
        layout.addWidget(self.sonuc_alanı)
        self.setLayout(layout)

    def baslat(self):
        if GOOGLE_AI_API_KEY == "YOUR_GOOGLE_AI_API_KEY":
            self.sonuc_alanı.setText(
                "HATA: Lütfen kod dosyasının en üstündeki "
                "'YOUR_GOOGLE_AI_API_KEY' alanına kendi Google AI API anahtarınızı girin."
            )
            return

        kurum_adi = self.kurum_input.text()
        domain = self.domain_input.text()
        unvan = self.unvan_input.text()

        if not kurum_adi or not domain:
            self.sonuc_alanı.setText('Lütfen Kurum Adı ve Domain alanlarını doldurun.')
            return

        self.ara_button.setDisabled(True)
        self.sonuc_alanı.clear()
        self.sonuc_alanı.setText(f"1. Adım: E-posta formatları aranıyor...\n")
        QApplication.processEvents()

        formatlar = self.mail_formati_bul(domain)
        self.sonuc_alanı.append(f"Bulunan Örnek Formatlar: {formatlar}\n")
        arama_metni = f"'{kurum_adi}'"
        if unvan:
            arama_metni += f" - '{unvan}'"
        self.sonuc_alanı.append(f"2. Adım: {arama_metni} pozisyonu için uluslararası çalışanlar aranıyor...\n")
        QApplication.processEvents()

        calisanlar = self.calisanlari_bul(kurum_adi, unvan)
        if not calisanlar:
            self.sonuc_alanı.append("Hiç çalışan bulunamadı veya arama limitine takıldı.")
            self.ara_button.setDisabled(False)
            return

        calisan_listesi_str = ", ".join([c['isim'] + ' ' + c['soyisim'] for c in calisanlar])
        self.sonuc_alanı.append(f"Bulunan Çalışanlar (Temizlenmiş): {calisan_listesi_str}\n")
        self.sonuc_alanı.append(f"3. Adım: Google AI (Gemini) ile e-posta adresleri üretiliyor...\n")
        QApplication.processEvents()

        uretilen_mailler = self.gemini_ile_mail_uret(domain, formatlar, calisanlar)
        self.sonuc_alanı.append("\n--- ÜRETİLEN E-POSTA ADRESLERİ ---\n")
        self.sonuc_alanı.append(uretilen_mailler)
        self.ara_button.setDisabled(False)

    def mail_formati_bul(self, domain):
        self.sonuc_alanı.append(f"'{domain}' için web'de arama yapılıyor...")
        QApplication.processEvents()
        return ["isim.soyisim", "i.soyisim", "isim", "isoyisim", "isim_soyisim"]

    def calisanlari_bul(self, kurum_adi, unvan):
        query = f'site:linkedin.com/in "{kurum_adi}"'
        if unvan:
            query += f' "{unvan}"'

        calisanlar = []
        try:
            for url in search(query, lang="en", num_results=15, sleep_interval=2.5):
                parts = url.split('/')
                if len(parts) > 4 and parts[3] == 'in':
                    # DÜZELTME: İsimleri ID'lerden ve rastgele eklerden temizleme
                    decoded_url_part = unquote(parts[4])
                    potential_name_parts = decoded_url_part.split('?')[0].replace('-', ' ').title().split(' ')

                    # Sadece harflerden oluşan kelimeleri alarak ID'leri ve diğer ekleri filtrele
                    clean_name_parts = [part for part in potential_name_parts if part.isalpha()]

                    if len(clean_name_parts) >= 2:
                        isim = clean_name_parts[0]
                        soyisim = " ".join(clean_name_parts[1:])
                        calisanlar.append({"isim": isim, "soyisim": soyisim})

        except Exception as e:
            self.sonuc_alanı.append(
                f"Çalışan arama hatası: {e}\n(Not: Çok sık arama yaparsanız Google geçici olarak engelleyebilir.)")
        return calisanlar

    def gemini_ile_mail_uret(self, domain, formatlar, calisanlar):
        if not self.model:
            hata_mesaji = "Google AI Modeli yüklenemedi. Lütfen API anahtarınızı kontrol edin."
            self.sonuc_alanı.append(hata_mesaji)
            return hata_mesaji

        calisan_str = "\n".join([f"- Ad: {c['isim']}, Soyad: {c['soyisim']}" for c in calisanlar])

        prompt = f"""
        Bir siber güvenlik ve OSINT (Açık Kaynak İstihbaratı) uzmanısın. Görevin, sağlanan bilgilere dayanarak potansiyel kurumsal e-posta adresleri oluşturmaktır.
        Kurum Domaini: {domain}
        Şirketin kullandığı bilinen e-posta kullanıcı adı formatları şunlardır:
        - {', '.join(formatlar)}
        (isim, i, soyisim, s gibi kısaltmaları kullanarak türetme yap)
        Aşağıdaki çalışan listesi için, yukarıdaki formatları kullanarak '@{domain}' uzantısıyla olası tüm e-posta adreslerini üret.
        Çalışan Listesi:
        {calisan_str}
        Cevabında sadece üretilen e-posta adresleri bulunsun. Her çalışan için bulduğun adresleri grupla. Başka hiçbir açıklama veya giriş cümlesi ekleme.
        Örnek Çıktı Formatı:
        İsmail Özkan:
        - ismail.ozkan@{domain}
        - i.ozkan@{domain}
        """

        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            return f"Google AI API isteği sırasında bir hata oluştu: {e}"


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = EmailFinderApp()
    window.show()
    sys.exit(app.exec())