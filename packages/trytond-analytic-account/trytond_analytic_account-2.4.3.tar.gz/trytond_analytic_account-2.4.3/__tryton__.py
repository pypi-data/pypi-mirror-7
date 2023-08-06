#This file is part of Tryton.  The COPYRIGHT file at the top level of
#this repository contains the full copyright notices and license terms.
{
    'name': 'Analytic Account',
    'name_bg_BG': 'Аналитична сметка',
    'name_ca_ES': 'Comptabilitat analítica',
    'name_de_DE': 'Kostenstellen',
    'name_es_AR': 'Contabilidad Analítica',
    'name_es_CO': 'Contabilidad Analítica',
    'name_es_ES': 'Contabilidad analítica',
    'name_fr_FR': 'Comptabilité analytique',
    'version': '2.4.3',
    'author': 'B2CK',
    'email': 'info@b2ck.com',
    'website': 'http://www.tryton.org/',
    'description': '''Financial and Accounting Module with:
    - Analytic accounting with any number of analytic charts

And with report:
    - Analytic account balance
''',
    'description_bg_BG': '''Финансов и счетоводен модул с:
    - Аналитично счетоводство с произволен брой аналитични графики

Прилежащи справки:
    - Баланс на аналитична сметка
''',
    'description_ca_ES': '''Mòdul financer i comptable amb:
    - Comptabilitat analítica amb plans analítics il·limitats

I amb informes:
    - Balanç comptable analític
''',
    'description_de_DE': '''Modul für Buchhhaltung mit:
    - Kostenstellen mit einer beliebigen Anzahl von Tabellen

Zugehörige Berichte:
    - Plan für Kostenstellen
''',
    'description_es_AR': '''Módulo financiero y de contabilidad con:
    - Contabilidad analítica con cualquier cantidad de planes analíticos

Y con informes:
    - Balance contable analítico
''',
    'description_es_CO': '''Módulo Financiero y de Contabilidad con:
    - Contabilidad Analítica con cualquier cantidad de planes analíticos

Y con reportes:
    - Balance Contable Analítico
''',
    'description_es_ES': '''Módulo financiero y contable con:
    - Contabilidad analítica con planes analíticos ilimitados

Y con informes:
    - Balance contable analítico
''',
    'description_fr_FR': '''Module comptable et financier, avec:
    - Comptabilité analytique autorisant un nombre arbitraire d'axes.

Et le rapport:
    - Balance comptable analytique
''',
    'depends': [
        'ir',
        'company',
        'currency',
        'account',
        'party',
        'res',
    ],
    'xml': [
        'analytic_account.xml',
        'account.xml',
        'line.xml',
    ],
    'translation': [
        'locale/bg_BG.po',
        'locale/ca_ES.po',
        'locale/cs_CZ.po',
        'locale/de_DE.po',
        'locale/es_AR.po',
        'locale/es_CO.po',
        'locale/es_ES.po',
        'locale/fr_FR.po',
        'locale/nl_NL.po',
        'locale/ru_RU.po',
    ],
}
