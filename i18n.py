"""
Internationalization (i18n) support for Flohmarkt
Handles multi-language support for Arabic and English
"""

import json
import os
from flask import session, request, current_app

class I18N:
    def __init__(self, app=None):
        self.app = app
        self.translations = {}
        self.default_language = 'ar'
        self.supported_languages = ['ar', 'en']
        
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize the i18n extension with Flask app"""
        self.app = app
        self.load_translations()
        
        # Add template globals
        app.jinja_env.globals['_'] = self.translate
        app.jinja_env.globals['get_current_language'] = self.get_current_language
        app.jinja_env.globals['get_supported_languages'] = lambda: self.supported_languages
        
        # Add template filters
        app.jinja_env.filters['currency'] = self.format_currency
    
    def load_translations(self):
        """Load all translation files"""
        translations_dir = os.path.join(os.path.dirname(__file__), 'translations')
        
        for lang in self.supported_languages:
            file_path = os.path.join(translations_dir, f'{lang}.json')
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    self.translations[lang] = json.load(f)
            except FileNotFoundError:
                print(f"Warning: Translation file {file_path} not found")
                self.translations[lang] = {}
    
    def get_current_language(self):
        """Get the current language from session or default"""
        return session.get('language', self.default_language)
    
    def set_language(self, language):
        """Set the current language in session"""
        if language in self.supported_languages:
            session['language'] = language
            session.permanent = True
            return True
        return False
    
    def translate(self, key, **kwargs):
        """
        Translate a key to the current language
        Supports nested keys with dot notation (e.g., 'navigation.home')
        """
        current_lang = self.get_current_language()
        
        # Get translation from loaded translations
        translation = self._get_nested_value(self.translations.get(current_lang, {}), key)
        
        # Fallback to default language if not found
        if translation is None and current_lang != self.default_language:
            translation = self._get_nested_value(self.translations.get(self.default_language, {}), key)
        
        # Final fallback to the key itself
        if translation is None:
            translation = key
        
        # Format translation with provided kwargs
        try:
            return translation.format(**kwargs)
        except (AttributeError, KeyError):
            return translation
    
    def _get_nested_value(self, data, key):
        """Get nested value from dictionary using dot notation"""
        keys = key.split('.')
        value = data
        
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return None
    
    def format_currency(self, amount):
        """Format currency based on current language"""
        current_lang = self.get_current_language()
        if current_lang == 'ar':
            return f"{amount:,.0f} ج.م"
        else:
            return f"EGP {amount:,.0f}"
    
    def get_language_direction(self):
        """Get text direction for current language"""
        return 'rtl' if self.get_current_language() == 'ar' else 'ltr'
    
    def get_language_code(self):
        """Get HTML language code for current language"""
        lang_codes = {
            'ar': 'ar',
            'en': 'en'
        }
        return lang_codes.get(self.get_current_language(), 'ar')

# Global instance
i18n = I18N()