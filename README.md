# myplacesbot

Разработка бота, который позволит сохранить места для будущего посещения.

Например, вы идете по улице, видите отличный ресторан, и хотите не забыть в него зайти в свободный вечер. 
Вам нужно каким-то образом отправить название места и его адрес, возможно приложить фотографию и заметку.  

В будущем, вы можете обратиться к боту и либо просто просмотреть список мест, которые вы раньше сохраняли, 
либо отправить текущее местоположение и получить самое ближайшее место.  

Для разработки этого бота необходимо сделать хранилище данных: базу даных или файлы. Также нужно 
использовать команды для бота и обмен сообщений с разным типом вложений.  

Бот должен реагировать на три команды:  
* /add – добавление нового места;
* /list – отображение добавленных мест;
* /reset - позволяет пользователю удалить все его добавленные локации (помним про [GDPR](https://en.wikipedia.org/wiki/General_Data_Protection_Regulation))  

Реализация команды /add доллжна быть двух уровней сложности:  
* указание адреса ресторана сразу в сообщении команды, в один шаг;
* пошаговое добавление места, с добавлением фото и локации.  

Команда /list в базовом варианте должна показывать 10 последних добавленных мест.  

Расширенная версия бота должна возвращать места в радиусе 500 метров при отправке локации, или возвращать сообщение об отсутствии добавленных мест.
Расчёт расстояния может производится по координатам при помощи математической формулы или любого удобного API.  

Не забыть учитывать пользователя, который добавляет места и возвращать ему только его сохраненные места.  

Бота можно загрузить на сервис Heroku, Amazon или любой другой. Для длительного хранения нужно подключить какую-нибудь SQL или NoSQL базу данных и использовать её.  