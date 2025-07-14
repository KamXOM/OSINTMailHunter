Kurumsal E-posta Bulucu
Bu araç, bir kurum adı ve domain bilgisi kullanarak o kurumdaki çalışanların olası e-posta adreslerini bulmak için yazılmış bir Python scriptidir.

İşleyiş
Uygulama, girdiğiniz bilgilere göre Google'da arama yaparak linkedin.com üzerinden çalışan isimleri bulur.

Daha sonra bu isimleri ve yaygın e-posta formatlarını (isim.soyisim@..., i.soyisim@... vb.) Google Gemini AI'a gönderir.

Yapay zeka, bu bilgilere dayanarak olası e-posta adreslerinin bir listesini oluşturur ve ekranda gösterir.

Kurulum
1. Gerekli Kütüphaneler:
Terminal veya komut satırına aşağıdaki komutu yazarak gerekli paketleri yükleyin.

Bash

pip install PyQt6 google-generativeai googlesearch-python
2. API Anahtarı:
Script'in çalışması için bir Google AI API anahtarına ihtiyacınız var. Kodu açın ve GOOGLE_AI_API_KEY değişkenine kendi anahtarınızı girin.

Python

# Google AI API Anahtarı
GOOGLE_AI_API_KEY = "BURAYA_KENDI_API_ANAHTARINIZI_YAPISTIRIN"
Kullanım
Script'i çalıştırın: python dosya_adi.py

Açılan penceredeki alanları doldurun (Kurum Adı, Unvan, Domain).

E-postaları Bul butonuna basın ve sonuçları bekleyin.

Uyarı
Bu aracı yasal ve etik sınırlar içinde kullanın. Aracın kullanımından doğacak sorumluluk kullanıcıya aittir.
