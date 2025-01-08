UI_CONFIG = {
    'title': 'Lanceur de Dés - Menu Principal',
    'welcome_text': 'Bienvenue dans le Lanceur de Dés',
    'buttons': [
        {
            'label': 'Dés Standards',
            'description': 'Lancez des dés classiques avec notation NdX',
            'handler': 'open_dice_frame'
        },
        {
            'label': 'Pièces',
            'description': 'Simulez des lancers de pièces',
            'handler': 'open_coins'
        },
        {
            'label': 'Dés Personnalisés',
            'description': 'Créez et utilisez vos propres dés',
            'handler': 'open_custom_dice'
        },
        {
            'label': 'Dés Runebound',
            'description': 'Dés spéciaux pour Runebound',
            'handler': 'open_runebound'
        },
        {
            'label': 'Statistiques',
            'description': 'Voir l\'historique des lancers',
            'handler': 'open_stats'
        }
    ]
}