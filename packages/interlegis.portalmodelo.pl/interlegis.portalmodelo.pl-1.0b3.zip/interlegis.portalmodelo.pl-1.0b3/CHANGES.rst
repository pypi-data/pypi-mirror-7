Changelog
=========

1.0b3 (2014-08-30)
------------------

- Added description to the folder structure.
  [jeanferri]


1.0b2 (2014-08-25)
------------------

- Corrige problema de serialização do DataGridField (refs. https://colab.interlegis.leg.br/ticket/2990)
  [marciomazza]

- Renomeia a URL da API Opendata de sapl-json para pl-json
  [jeanferri]

- Corrige o link @@mesa-diretora para usuários anônimos
  [jeanferri]

- Alterado o widget do campo description (bio) de um parlamentar para WysiwygFieldWidget (refs. https://colab.interlegis.leg.br/ticket/2928).
  [ericof]

- Adicionado campo email para um parlamentar (refs. https://colab.interlegis.leg.br/ticket/2928).
  [ericof]

- Adicionado campo site para um parlamentar (refs. https://colab.interlegis.leg.br/ticket/2928).
  [ericof]


1.0b1 (2014-07-02)
------------------

- O widget utilizado no campo ``birthday`` foi mudado (refs. https://colab.interlegis.leg.br/ticket/2927).
  [hvelarde]


1.0a3 (2014-04-25)
------------------

- Depend on interlegis.portalmodelo.api.

- Fix menu item registration.

- Fix tags closing on ``session_view.pt``.


1.0a2 (2014-04-08)
------------------

- Fix dependency inclusion to avoid ``ConfigurationError: ('Invalid
  directive', u'factory')``.

- Update package dependencies.

- Disallow comments on package content types.

- Allow creation of the sub-structure if we already have a folder named
  Processo Legislativo.

- Remove layout from folder at uninstall time.

- Fix different views and update translations.

- Fix JSON import.


1.0a1 (2014-04-06)
------------------

- Initial release.
