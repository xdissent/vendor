@echo off
set VIRTUAL_ENV=__VIRTUAL_ENV__

if not defined PROMPT (
    set PROMPT=$P$G
)

if defined _OLD_VIRTUAL_PROMPT (
    set PROMPT=%_OLD_VIRTUAL_PROMPT%
)

set _OLD_VIRTUAL_PROMPT=%PROMPT%
set PROMPT=(__VIRTUAL_NAME__) %PROMPT%

if defined _OLD_VIRTUAL_PATH (
    set PATH=%_OLD_VIRTUAL_PATH%
    goto SKIPPATH
)
set _OLD_VIRTUAL_PATH=%PATH%

:SKIPPATH
set PATH=%VIRTUAL_ENV%\\__BIN_NAME__;%PATH%

:END
