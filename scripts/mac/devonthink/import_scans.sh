#!/usr/bin/env bash

AUTOMATION_FOLDER=~/Documents/Private/automation

cd ${AUTOMATION_FOLDER}/paper-archive
~/go/bin/drive pull -quiet Inbox


if [ "$(ls -A Inbox)" ]; then
  osascript ${AUTOMATION_FOLDER}/src/python/scripts/mac/devonthink/import_pdfs_and_ocr.scpt ${AUTOMATION_FOLDER}/paper-archive/Inbox/ "1. Paper Archive" "/Inbox"

  mv Inbox/* Outbox
  ~/go/bin/drive push -quiet Inbox
fi

cd -