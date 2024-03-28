@Echo off
setlocal EnableExtensions EnableDelayedExpansion

set "str=#define"
set "str2=xu"
set "str3=xu"
set Lhs=u
set Rhs="HELLOe"
(
echo class OD:
for /f "tokens=1-3" %%A in (gen_indices.h) do (
  if %str% == %%A (
    set "c=%%C "
rem    echo !c!
    set "d=%%C "
rem    echo !d!
    set "d=!d:~-2,-1!"
rem    echo !d!
rem    set Rhs=d
rem    echo !d!
    set "e=!c:~0,-2!"
    set "c=!c:~0,-1!"
rem    echo !e!
rem    if %str3% == %str2%
rem    echo !Lhs!
rem (echo Equal) else (echo Not Equal)
    if !Lhs! == !d! (
      echo   %%B = !e! ) else (
      echo   %%B = !c! )
  )
))>.\gen_indices.py
rem (
rem set "strDefGet=  def get(x):"
rem set "strReturn=    return x"
rem echo.
rem echo !strDefGet!
rem echo !strReturn!
rem )>>.\gen_indices.py