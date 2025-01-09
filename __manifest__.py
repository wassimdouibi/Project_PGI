# -*- coding: utf-8 -*-
{
    'name': "Plateforme intégrée de Gestion des Réclamations",

    'summary': """
        Amélioration du service de réclamation client pour l'entreprise AlMiyah Djazair
    """,

    'description': """
        Gestion de réclamation module pour :
            - Recensement des réclamations
            - Traitement des réclamations
            - Communication avec le réclamant
            - Indicateurs de performance
    """,

    'author': "G1_Equipe4",
    'website': "http://www.G1_Equipe4.com",

    # Categories can be used to filter modules in modules listing
    'category': 'Reclamation',
    'version': '1.0',

    # any module necessary for this one to work correctly
    'depends': [
        'base',
        # Project Module
        'project',
        # Survey Module
        'survey',
        # Dashboards Module
        'board'
    ],

    # always loaded
    'data': [
        # Access Rights
        'security/security.xml',
        'security/ir.model.access.csv',
        # 'templates.xml',
        # 'data/report_reclamation.xml',
        'views/reclamation_views.xml',
    ],

    # 'views': [
    #   'views/reclamation_views.xml',
    #     'views/accuse_reclamation_template.xml',
    # ],
    
    # only loaded in demonstration mode
    'demo': [
        'demo.xml',
    ],
}
