# UniversalSynSaveInstance — versão própria

Versão própria com `loadstring`, dependências principais locais e correções de compatibilidade para compressão e atualização do API dump.

## Uso

```lua
local synsaveinstance = loadstring(game:HttpGet(
    "https://raw.githubusercontent.com/luaaaaagkkkkkkk/UniversalSynSaveInstance-Custom/main/saveinstance.luau",
    true
), "saveinstance")()

local SaveInstanceOptions = {}
synsaveinstance(SaveInstanceOptions)
```

O módulo requer um executor compatível com `loadstring`, `game:HttpGet`, `buffer` e as APIs opcionais escolhidas. O endpoint beta `zbeta` pode responder 401 sem autorização; o script trata isso como fallback opcional e tenta os endpoints públicos/cached disponíveis.

Consulte [`LICENSE`](LICENSE) para os termos e atribuições.
