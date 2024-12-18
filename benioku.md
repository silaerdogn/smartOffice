# Akıllı Ofis Güvenlik ve İzleme Sistemi
Merhaba! Biz, ofis alanlarının güvenliğini ve verimliliğini artırmak için akıllı bir sistem oluşturmak üzere yola çıktık. İşte böylece "Akıllı Ofis Güvenlik ve İzleme Sistemi" projemiz doğdu.

# Proje Genel Bakış
Projemizin temel amacı, ofis ortamının güvenliğini sağlamak, çalışanların konforunu artırmak ve yöneticilere ofis hakkında gerçek zamanlı bilgiler sunmaktır. Bunu başarmak için Raspberry Pi'yi merkezi kontrol ünitesi olarak kullandık ve çeşitli sensörler, veritabanı bağlantısı ve bulut hizmetleriyle entegre ederek kapsamlı bir çözüm oluşturduk.

# Proje Bileşenleri
Sistemimiz, ofis içindeki farklı alanları ve işlevleri kapsamaktadır:

# 1. Ana Giriş Kontrolü
Ofise giriş yapmak için çalışanların bir tuş takımı kullanarak şifre girmesi gerekmektedir. Girilen şifre, Amazon RDS veritabanında doğrulanır. Şifre doğruysa, yeşil bir LED yanar ve LCD ekranda "Hoş geldiniz @isim" mesajı görüntülenir. Şifre yanlışsa, kırmızı bir LED görsel bir uyarı verir. Başarılı kimlik doğrulamasının ardından, devam takip sistemi otomatik olarak tetiklenir.

Ana giriş kontrolü için kod, giris.py dosyasında bulunabilir. Tuş takımı girişini, veritabanı doğrulamasını ve LCD ekran yönetimini sağlar. db_operations.py dosyası, veritabanı bağlantısı ve işlemleri için gerekli fonksiyonları içerir.

# 2. Müdür Odası Kontrolü
Müdür odasına erişim, yüz tanıma teknolojisi kullanılarak kontrol edilir. Veritabanında kayıtlı olan müdürün yüzü algılandığında, bir servo motor kapıyı açar. Bu, yalnızca yetkili kişilerin müdür odasına girebilmesini sağlar.

mudur_yonetimi.py dosyası, müdür odası kontrolü için kodu içerir. Yüz tanıma sistemini ve servo motor kontrolünü sağlar. Yüz tanıma modeli, manager_images dizininde saklanan görüntüler kullanılarak eğitilir.

# 3. Ana Salon İzleme
Ofis ortamındaki sıcaklık ve nem seviyeleri, bir sıcaklık/nem sensörü kullanılarak sürekli olarak izlenir. Ölçülen değerler, gerçek zamanlı olarak LCD ekranda görüntülenir ve çalışanlar için optimal çalışma koşullarının sağlanmasına yardımcı olur.

Ana salon izleme için kod, salon.py dosyasında bulunabilir. Sıcaklık/nem sensöründen verileri okur ve LCD ekranda görüntüler. dht11.py dosyası, DHT11 sensörüyle etkileşim kurmak için gerekli fonksiyonları sağlar.

# 4. Mutfak Güvenliği
Mutfaktaki olası gaz kaçaklarını tespit etmek için bir MQ2 gaz sensörü kullanılır. Tehlikeli bir gaz seviyesi algılandığında, bir buzzer kullanılarak sesli bir alarm tetiklenir. Bu erken uyarı sistemi, kazaları önlemeye ve ofisin güvenliğini sağlamaya yardımcı olur.

mutfak.py dosyası, mutfak güvenliği için kodu içerir. MQ2 gaz sensöründen verileri okur ve eşik değeri aşıldığında buzzeri etkinleştirir. mq2.py dosyası, MQ2 sensörüyle etkileşim kurmak için gerekli fonksiyonları sağlar.

# 5. Tuvalet Doluluğu
Tuvaletlerin doluluk durumu, bir hareket sensörü kullanılarak belirlenir. Tuvalet kapısı açıldığında, sensör hareketi algılar ve bir LED yanar. Ayrıca, tuvalet durumu LCD ekranda "Tuvalet Dolu/Boş" olarak görüntülenir. Bu özellik, gereksiz beklemeyi önler ve ofis trafiğini optimize eder.

Tuvalet doluluğu için kod, lavabo.py dosyasında bulunabilir. Hareket sensöründen verileri okur, LED'i kontrol eder ve LCD ekranı buna göre günceller. pir.py dosyası, PIR hareket sensörüyle etkileşim kurmak için gerekli fonksiyonları sağlar.

# 6. Toplantı Odası
Toplantı odası da bir hareket sensörüyle donatılmıştır. Odada hareket algılandığında, bir LED ışığı yanar ve odanın dolu olduğunu gösterir. Bu, çalışanların toplantı odası kullanımını takip etmelerine ve buna göre planlamalarına olanak tanır.

toplantiodasi.py dosyası, toplantı odası kontrolü için kodu içerir. Hareket sensöründen verileri okur ve doluluk durumuna göre LED'i kontrol eder. pir.py dosyası, PIR hareket sensörüyle etkileşim kurmak için kullanılır.

# Kullanılan Teknolojiler
Projemizde çeşitli donanım bileşenleri ve yazılım teknolojileri kullandık:

Raspberry Pi: Merkezi kontrol ünitesi olarak görev yapar.
Çeşitli sensörler: Hareket, sıcaklık/nem, gaz sensörleri vb.
LCD ekranlar: Bilgileri görüntülemek için kullanılır.
LED'ler ve buzzer: Görsel ve işitsel geri bildirim sağlar.
Servo motor: Kapı kontrolü için kullanılır.
Amazon RDS: Veritabanı yönetimi için kullanılır.
AWS IoT Core: Bulut tabanlı veri işleme ve analiz için kullanılır.
Python programlama dili: Sistemin yazılım geliştirmesi için kullanılır.
Kurulum ve Kullanım
Sistemimizi kurmak ve kullanmak oldukça basittir. Adım adım kurulum talimatları ve kapsamlı belgeler GitHub depomuzda mevcuttur. Raspberry Pi'nizi hazırlayın, gerekli bileşenleri bağlayın, yazılımı yükleyin ve sistemi yapılandırın. Sistemi başlattıktan sonra, ofis ortamınız akıllı bir şekilde izlenecek ve kontrol edilecektir.

#  Akıllı Ofis İzleme Paneli
Projemizin en heyecan verici özelliklerinden biri de web tabanlı izleme panelidir. Panele akilliofisin.com adresinden erişebilirsiniz. Panel, ofis yöneticilerine ve yetkili personele gerçek zamanlı veriler ve içgörüler sağlar.

# Panel aracılığıyla şunları görüntüleyebilirsiniz:

- Ofiste o anda kimlerin bulunduğu
- Gaz sensörü durumu ve uyarıları
- Toplantı odasının doluluk durumu
- Ofisteki son aktiviteler
- Ofisteki toplam kişi sayısı
Bu bilgiler, ofis yönetimini optimize etmenize, kaynakları verimli bir şekilde kullanmanıza ve olası sorunları hızlı bir şekilde tespit etmenize yardımcı olur.

Web sitemizde ayrıca bir iletişim sayfası bulunmaktadır. Herhangi bir sorunuz, geri bildiriminiz veya desteğe ihtiyacınız olursa, akilliofisin.com/iletisim adresinden bize ulaşabilirsiniz. Ekibimiz size yardımcı olmaktan mutluluk duyacaktır.

# #  Sonuç
"Akıllı Ofis Güvenlik ve İzleme Sistemi" projemiz, modern ofislerin ihtiyaçlarını karşılamak üzere tasarlanmış kapsamlı bir çözümdür. Güvenliği artırır, verimliliği yükseltir ve ofis yönetimini basitleştirir. Raspberry Pi, çeşitli sensörler, bulut hizmetleri ve özel olarak geliştirdiğimiz yazılımın gücünü birleştirerek, ofisleri akıllı ve bağlantılı alanlara dönüştürüyoruz.

Projemiz açık kaynaklıdır ve GitHub'da mevcuttur. Sizleri de katkıda bulunmaya, geri bildirim sağlamaya ve projeyi kendi gereksinimlerinize uygun hale getirmeye davet ediyoruz.

"Akıllı Ofis Güvenlik ve İzleme Sistemi" ile ofislerinizi geleceğe taşıyın. Daha fazla bilgi için web sitemizi akilliofisin.com ziyaret edin ve bu heyecan verici yolculuğa bize katılın!

#  İletişim:

Web sitesi: akilliofisin.com
İletişim: akilliofisin.com/iletisim
GitHub: github.com/ahmetmertkabak/smartOffice
Daha iyi bir gelecek için akıllı ofisler yaratmada bize katılın!
