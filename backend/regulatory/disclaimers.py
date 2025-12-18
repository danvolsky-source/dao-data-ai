"""
Regulatory Disclaimer Content
Standard disclaimers for all prediction and analytical outputs
"""

# Primary Regulatory Disclaimer
MAIN_DISCLAIMER = """
⚠️ IMPORTANT RISK AND LIMITATION NOTICE

Information on this platform is provided exclusively for 
informational and educational purposes. This is NOT:
- Investment advice
- Trading signals
- Financial recommendations
- A guarantee of future results

LIMITATIONS AND RISKS:
1. Predictions are based on historical data and may be inaccurate
2. Past performance does not guarantee future results
3. Only public data from official sources is used
4. Sentiment analysis may not reflect actual community opinion
5. ML models are experimental and may contain errors

RECOMMENDATIONS:
- DO NOT use this information for making trading decisions
- Conduct your own research (DYOR)
- Consult with qualified financial advisors
- Only invest funds you can afford to lose

All risks are borne by the user. We are not responsible for any losses
arising from use of this platform.
"""

# Short Disclaimer for API Responses
SHORT_DISCLAIMER = (
    "⚠️ This is analytical information, not investment advice. "
    "Use for educational purposes only. All risks are borne by the user."
)

# Prediction-Specific Disclaimer
PREDICTION_DISCLAIMER = (
    "Этот прогноз основан на ML модели и исторических данных. "
    "Точность не гарантирована. НЕ используйте для торговых решений. "
    "Confidence score показывает уверенность модели, но не является гарантией."
)

# Sentiment Analysis Disclaimer
SENTIMENT_DISCLAIMER = (
    "Анализ настроений основан на публичных сообщениях и может не отражать "
    "реальное мнение всего сообщества. Используйте как один из многих факторов "
    "в вашем исследовании. Не является инвестиционным советом."
)

# Model Performance Disclaimer
MODEL_DISCLAIMER = (
    "Метрики модели основаны на бэктестинге исторических данных. "
    "Прошлая производительность не гарантирует будущие результаты. "
    "Модели регулярно обновляются и могут изменяться."
)

# Live Tracking Disclaimer
LIVE_TRACKING_DISCLAIMER = (
    "Live tracking показывает фактическую производительность модели на "
    "завершенных предложениях. Это для прозрачности и не является "
    "гарантией будущей точности."
)

# Data Source Disclaimer
DATA_SOURCE_DISCLAIMER = (
    "Все данные получены из публичных источников: Snapshot, Tally, Discord, "
    "форумы сообщества. Мы не гарантируем полноту или точность данных. "
    "Всегда проверяйте информацию в первоисточниках."
)

# Confidence Threshold Message
CONFIDENCE_THRESHOLD_MESSAGE = (
    "Прогнозы с confidence score ниже 85% могут быть недостаточно надежными. "
    "Используйте такие прогнозы с особой осторожностью."
)

# Terms of Service Summary
TOS_SUMMARY = """
УСЛОВИЯ ИСПОЛЬЗОВАНИЯ (КРАТКАЯ ВЕРСИЯ)

1. НАЗНАЧЕНИЕ СЕРВИСА
   Платформа предназначена для анализа и исследования данных DAO.
   Это инструмент для образования, а не для торговли.

2. НЕТ ФИНАНСОВЫХ СОВЕТОВ
   Мы не предоставляем финансовые, инвестиционные или юридические консультации.
   Пользователи должны проконсультироваться с квалифицированными специалистами.

3. ОГРАНИЧЕНИЕ ОТВЕТСТВЕННОСТИ
   Мы не несем ответственности за любые убытки, возникшие в результате
   использования платформы или доверия к предоставленной информации.

4. ЭКСПЕРИМЕНТАЛЬНАЯ ПРИРОДА
   ML модели и аналитика являются экспериментальными. Они могут содержать
   ошибки и неточности. Не полагайтесь исключительно на них.

5. ПУБЛИЧНЫЕ ДАННЫЕ
   Мы используем только публично доступные данные. Пользователи несут
   ответственность за проверку точности информации.

6. ИЗМЕНЕНИЯ В СЕРВИСЕ
   Мы оставляем за собой право изменять, приостанавливать или прекращать
   любую часть сервиса в любое время без предварительного уведомления.

Используя эту платформу, вы соглашаетесь с этими условиями.
"""

# Privacy Policy Summary
PRIVACY_SUMMARY = """
ПОЛИТИКА КОНФИДЕНЦИАЛЬНОСТИ (КРАТКАЯ ВЕРСИЯ)

1. СБОР ДАННЫХ
   Мы собираем минимально необходимые данные:
   - IP адреса (для безопасности и аудита)
   - User agents (для технической поддержки)
   - Запросы API (для улучшения сервиса)
   - Wallet addresses (только если вы подключаете кошелек)

2. ИСПОЛЬЗОВАНИЕ ДАННЫХ
   Данные используются для:
   - Предоставления и улучшения сервиса
   - Обеспечения безопасности
   - Соблюдения требований регуляторов
   - Аналитики и исследований

3. ХРАНЕНИЕ ДАННЫХ
   - Данные хранятся в защищенной базе данных (Supabase)
   - Применяется шифрование при передаче и хранении
   - Доступ ограничен авторизованным персоналом

4. РАСКРЫТИЕ ДАННЫХ
   Мы не продаем ваши данные третьим лицам.
   Раскрытие возможно только:
   - По требованию регуляторов
   - Для предотвращения мошенничества
   - С вашего явного согласия

5. ВАШИ ПРАВА
   Вы имеете право:
   - Запросить доступ к вашим данным
   - Запросить удаление данных
   - Отозвать согласие на обработку

Для вопросов по конфиденциальности: privacy@daodataai.com
"""


def get_full_disclaimer() -> str:
    """Return complete disclaimer text"""
    return MAIN_DISCLAIMER


def get_api_disclaimer(disclaimer_type: str = "short") -> str:
    """
    Get appropriate disclaimer for API response
    
    Args:
        disclaimer_type: Type of disclaimer ('short', 'prediction', 'sentiment', 'model', 'tracking')
    
    Returns:
        Appropriate disclaimer text
    """
    disclaimers = {
        "short": SHORT_DISCLAIMER,
        "prediction": PREDICTION_DISCLAIMER,
        "sentiment": SENTIMENT_DISCLAIMER,
        "model": MODEL_DISCLAIMER,
        "tracking": LIVE_TRACKING_DISCLAIMER,
        "data": DATA_SOURCE_DISCLAIMER
    }
    
    return disclaimers.get(disclaimer_type, SHORT_DISCLAIMER)


def get_confidence_warning(confidence: float) -> str:
    """
    Get warning message based on confidence score
    
    Args:
        confidence: Model confidence score (0-1)
    
    Returns:
        Warning message if confidence is low
    """
    if confidence < 0.85:
        return CONFIDENCE_THRESHOLD_MESSAGE
    return ""


def wrap_response_with_disclaimer(data: dict, disclaimer_type: str = "short") -> dict:
    """
    Wrap API response with appropriate disclaimer
    
    Args:
        data: Response data
        disclaimer_type: Type of disclaimer to include
    
    Returns:
        Response dict with disclaimer
    """
    return {
        "disclaimer": get_api_disclaimer(disclaimer_type),
        "data": data,
        "terms": "By using this data, you agree to our Terms of Service",
        "privacy": "See our Privacy Policy for data handling practices"
    }
