#!/bin/bash

bin/i18ndude rebuild-pot --pot src/collective/jazzport/locales/collective.jazzport.pot --merge src/collective/jazzport/locales/manual.pot --create collective.jazzport src/collective/jazzport

bin/i18ndude sync --pot src/collective/jazzport/locales/collective.jazzport.pot src/collective/jazzport/locales/*/LC_MESSAGES/collective.jazzport.po
