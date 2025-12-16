# Sentry Setup Instructions

## 🎯 Цель
Настроить error monitoring для отслеживания ошибок в production.

## ✅ Уже сделано:
- ✅ Добавлена зависимость `@sentry/nextjs` в package.json
- ✅ Создан `sentry.client.config.js` (client-side tracking)
- ✅ Создан `sentry.server.config.js` (server-side tracking)
- ✅ Создан `.env.local.example` с переменными
- ✅ Настроен `next.config.js`

## 📋 Что осталось сделать:

### Шаг 1: Получить Sentry DSN

1. Перейти на **https://sentry.io**
2. Зарегистрироваться или войти в аккаунт
3. Нажать **Create Project**
4. Выбрать платформу: **Next.js**
5. Задать имя проекта: `dao-data-ai`
6. Скопировать **DSN** (выглядит как):
   ```
   https://xxxxxxxxxxxxx@oxxxxx.ingest.sentry.io/xxxxxxx
   ```

### Шаг 2: Добавить DSN в Vercel Environment Variables

1. Перейти в **Vercel Dashboard**:
   - https://vercel.com/dans-projects-be7275a1/dao-data-ai/settings/environment-variables

2. Нажать **Add New** → **Environment Variable**

3. Заполнить поля:
   - **Key**: `NEXT_PUBLIC_SENTRY_DSN`
   - **Value**: ваш DSN из Sentry
   - **Environments**: выбрать **Production**, **Preview**, **Development**

4. Нажать **Save**

5. **Redeploy** последний deployment для применения изменений

### Шаг 3: Проверить работу Sentry

1. Открыть https://www.sky-mind.com
2. Открыть DevTools (F12) → Console
3. Вызвать тестовую ошибку:
   ```javascript
   throw new Error("Sentry test error")
   ```
4. Проверить, что ошибка появилась в Sentry Dashboard

## 🔧 Альтернативный способ (для тестирования без Sentry)

Если не хотите пока регистрироваться в Sentry:

1. Закомментировать импорты Sentry в конфигах:
   - `sentry.client.config.js`
   - `sentry.server.config.js`

2. Или просто не добавлять `NEXT_PUBLIC_SENTRY_DSN` в Vercel
   - Dashboard будет работать без Sentry

## ✨ После настройки

Sentry будет автоматически отслеживать:
- ❌ JavaScript errors
- 🐛 Unhandled promise rejections  
- 🔍 API errors
- 📊 Performance issues
- 🎬 Session replays (10% всех сессий + 100% с ошибками)

## 📚 Полезные ссылки

- Sentry Docs: https://docs.sentry.io/platforms/javascript/guides/nextjs/
- Vercel Environment Variables: https://vercel.com/docs/concepts/projects/environment-variables
