# UniversalSynSaveInstance — versão própria

Versão própria com `loadstring`, dependências principais locais, progresso detalhado na UI e correções de compatibilidade para compressão e atualização do API dump.

## Uso

```lua
local synsaveinstance = loadstring(game:HttpGet(
    "https://raw.githubusercontent.com/luaaaaagkkkkkkk/UniversalSynSaveInstance-Custom/main/saveinstance.luau",
    true
), "saveinstance")()

local SaveInstanceOptions = {}
synsaveinstance(SaveInstanceOptions)
```

A compressão fica desativada por padrão para evitar travamentos em executores que implementam zstd/lz4 de forma instável; ela pode ser ativada explicitamente com `CompressionMode = "zstd"` ou `CompressionMode = "lz4"`.

O módulo requer um executor compatível com `loadstring`, `game:HttpGet`, `buffer` e as APIs opcionais escolhidas. O endpoint beta `zbeta` pode responder 401 sem autorização; o script trata isso como fallback opcional e tenta os endpoints públicos/cached disponíveis.

Consulte [`LICENSE`](LICENSE) para os termos e atribuições.


## Perfil rápido e perfil completo

O padrão prioriza velocidade: não faz decompilação, não recupera scripts publicados como assets e ignora propriedades ocultas do executor. Isso pode deixar `Source` sem o código original e omitir algumas propriedades especiais.

Para priorizar completude em vez de velocidade:

```lua
synsaveinstance({
    Decompile = true,
    RecoverScriptsFromAssets = true,
    IgnoreSpecialProperties = false,
    DecompileTimeout = 10,
})
```
