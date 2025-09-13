// Переключение белого хедера на странице корзины
(function(){
  try {
    const isCart = window.location.pathname.startsWith('/cart');
    const navbar = document.querySelector('.navbar');
    if (isCart && navbar) {
      navbar.classList.add('navbar--white');
    }
  } catch (e) {}
})();

// Система уведомлений с пчёлкой
class NotificationSystem {
  constructor() {
    this.notification = null;
    this.timeout = null;
  }

  show(message, duration = 3000) {
    console.log('NotificationSystem.show called with message:', message);
    
    // Удаляем предыдущее уведомление если есть
    this.hide();

    // Создаем новое уведомление
    this.notification = document.createElement('div');
    this.notification.className = 'notification';
    this.notification.innerHTML = `
      <div class="bee-icon"></div>
      <div class="message">${message}</div>
    `;

    console.log('Created notification element:', this.notification);

    // Добавляем в DOM
    document.body.appendChild(this.notification);
    console.log('Added notification to DOM');

    // Показываем с небольшой задержкой для плавности
    setTimeout(() => {
      this.notification.classList.add('show');
      console.log('Added show class to notification');
    }, 100);

    // Автоматически скрываем через указанное время
    this.timeout = setTimeout(() => {
      this.hide();
    }, duration);
  }

  hide() {
    if (this.notification) {
      // Добавляем класс hiding для плавного ухода за экран
      this.notification.classList.remove('show');
      this.notification.classList.add('hiding');
      
      // Удаляем из DOM после анимации
      setTimeout(() => {
        if (this.notification && this.notification.parentNode) {
          this.notification.parentNode.removeChild(this.notification);
        }
        this.notification = null;
      }, 1200); // Время соответствует CSS transition
    }

    if (this.timeout) {
      clearTimeout(this.timeout);
      this.timeout = null;
    }
  }
}

// Создаем глобальный экземпляр системы уведомлений
window.notificationSystem = new NotificationSystem();
console.log('Notification system initialized');

// Показываем уведомления только для сообщений о корзине
(function() {
  try {
    // Ищем сообщения Django в DOM, связанные с корзиной
    const messages = document.querySelectorAll('.messages .alert, .messages .alert-success, .messages .alert-error, .messages .alert-info');
    
    messages.forEach(message => {
      const text = message.textContent.trim();
      if (text && (
        text.includes('корзин') || 
        text.includes('товар') || 
        text.includes('добавлен') || 
        text.includes('удален') ||
        text.includes('перенесены')
      )) {
        // Определяем тип сообщения
        let duration = 3000;
        if (message.classList.contains('alert-error')) {
          duration = 5000; // Ошибки показываем дольше
        }
        
        // Показываем уведомление
        window.notificationSystem.show(text, duration);
        
        // Скрываем оригинальное сообщение
        message.style.display = 'none';
      }
    });
  } catch (e) {
    console.log('Notification system error:', e);
  }
})();

// Обработка кликов по кнопкам корзины
(function() {
  try {
    // Обрабатываем клики по кнопкам добавления в корзину
    document.addEventListener('click', function(e) {
      // Ищем кнопки с классом cart-button или ссылки на добавление в корзину
      const target = e.target.closest('a[href*="/cart/add/"], .cart-button');
      if (target) {
        console.log('Cart button clicked:', target.href);
        e.preventDefault();
        
        // Показываем уведомление сразу при клике
        window.notificationSystem.show('Товар добавлен в корзину', 3000);
        
        // Выполняем запрос
        fetch(target.href)
          .then(response => {
            console.log('Cart response:', response.status);
            if (response.ok) {
              // Обновляем счетчик корзины если есть
              updateCartCounter();
              // Перенаправляем только после того, как уведомление полностью показалось
              setTimeout(() => {
                window.location.href = target.href;
              }, 3500); // 3.5 секунды - время показа уведомления + небольшая задержка
            } else {
              // Показываем уведомление об ошибке
              window.notificationSystem.show('Ошибка при добавлении товара', 5000);
              // Перенаправляем после показа ошибки
              setTimeout(() => {
                window.location.href = target.href;
              }, 5500);
            }
          })
          .catch(error => {
            console.log('Error adding to cart:', error);
            // Показываем уведомление об ошибке
            window.notificationSystem.show('Ошибка при добавлении товара', 5000);
            // Перенаправляем после показа ошибки
            setTimeout(() => {
              window.location.href = target.href;
            }, 5500);
          });
      }
    });
  } catch (e) {
    console.log('Cart click handler error:', e);
  }
})();

// Функция обновления счетчика корзины
function updateCartCounter() {
  try {
    // Здесь можно добавить логику обновления счетчика корзины
    // Например, сделать AJAX запрос для получения количества товаров
  } catch (e) {
    console.log('Cart counter update error:', e);
  }
}

// Обработка кликов по кнопкам изменения количества
(function() {
  try {
    document.addEventListener('click', function(e) {
      const target = e.target.closest('a[href*="/cart/qty/"]');
      if (target) {
        e.preventDefault();
        
        // Показываем уведомление о изменении количества
        const isIncrease = target.href.includes('/inc/');
        const message = isIncrease ? 'Количество увеличено' : 'Количество уменьшено';
        window.notificationSystem.show(message, 500);
        
        // Выполняем запрос
        fetch(target.href)
          .then(response => {
            if (response.ok) {
              // Обновляем страницу после показа уведомления
              setTimeout(() => {
                window.location.reload();
              }, 600); // 0.6 секунды - время показа уведомления + небольшая задержка
            } else {
              window.notificationSystem.show('Ошибка при изменении количества', 1500);
            }
          })
          .catch(error => {
            console.log('Error changing quantity:', error);
            window.notificationSystem.show('Ошибка при изменении количества', 3000);
          });
      }
    });
  } catch (e) {
    console.log('Quantity change handler error:', e);
  }
})();

// Обработка кликов по кнопкам удаления
(function() {
  try {
    document.addEventListener('click', function(e) {
      const target = e.target.closest('a[href*="/cart/remove/"]');
      if (target) {
        e.preventDefault();
        
        // Показываем уведомление об удалении
        window.notificationSystem.show('Товар удален из корзины', 500);
        
        // Выполняем запрос
        fetch(target.href)
          .then(response => {
            if (response.ok) {
              // Обновляем страницу после показа уведомления
              setTimeout(() => {
                window.location.reload();
              }, 600); // 0.6 секунды - время показа уведомления + небольшая задержка
            } else {
              window.notificationSystem.show('Ошибка при удалении товара', 1500);
            }
          })
          .catch(error => {
            console.log('Error removing item:', error);
            window.notificationSystem.show('Ошибка при удалении товара', 1500);
          });
      }
    });
  } catch (e) {
    console.log('Remove item handler error:', e);
  }
})();


