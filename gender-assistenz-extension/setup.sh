#!/bin/bash
rm gender_assist.oxt
zip -r gender_assist.oxt *
/Applications/LibreOffice.app/Contents/MacOS/unopkg remove gender_assist.oxt
/Applications/LibreOffice.app/Contents/MacOS/unopkg add gender_assist.oxt
/Applications/LibreOffice.app/Contents/MacOS/soffice --writer